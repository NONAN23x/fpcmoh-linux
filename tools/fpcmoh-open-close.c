/* SPDX-License-Identifier: LGPL-2.1-or-later */
/*
 * Minimal live probe for libfprint MR !570 and FPC 10a5:9200.
 *
 * This program intentionally performs only libfprint discovery, device open,
 * and device close. The fpcmoh open path initializes a volatile MI_00 session,
 * retrieves/verifies the existing TLS key, and performs the TLS handshake.
 * It does not enroll, verify, arm for capture, request an image, replace or
 * flush keys, clear storage, or access the MI_01 firmware interface.
 */

#include <stdlib.h>

#include <glib.h>
#include <fprint.h>

#define PROBE_TIMEOUT_SECONDS 30

typedef struct
{
  GCancellable *cancellable;
  gboolean      fired;
} ProbeTimeout;

static gboolean
cancel_probe (gpointer user_data)
{
  ProbeTimeout *timeout = user_data;

  timeout->fired = TRUE;
  g_printerr ("Probe timeout reached; cancelling the pending operation.\n");
  g_cancellable_cancel (timeout->cancellable);

  return G_SOURCE_REMOVE;
}

static gboolean
run_close (FpDevice *device)
{
  g_autoptr(GCancellable) cancellable = g_cancellable_new ();
  g_autoptr(GError) error = NULL;
  ProbeTimeout timeout = { cancellable, FALSE };
  guint timeout_id;
  gboolean closed;

  timeout_id = g_timeout_add_seconds (PROBE_TIMEOUT_SECONDS,
                                      cancel_probe,
                                      &timeout);
  closed = fp_device_close_sync (device, cancellable, &error);

  if (!timeout.fired)
    g_source_remove (timeout_id);

  if (!closed)
    {
      g_printerr ("CLOSE_FAILED: %s\n",
                  error != NULL ? error->message : "unknown error");
      return FALSE;
    }

  g_print ("CLOSE_OK\n");
  return TRUE;
}

int
main (void)
{
  g_autoptr(FpContext) context = NULL;
  g_autoptr(GCancellable) cancellable = NULL;
  g_autoptr(GError) error = NULL;
  GPtrArray *devices;
  FpDevice *target = NULL;
  ProbeTimeout timeout;
  guint timeout_id;
  gboolean opened;

  context = fp_context_new ();
  devices = fp_context_get_devices (context);

  for (guint i = 0; i < devices->len; i++)
    {
      FpDevice *candidate = g_ptr_array_index (devices, i);

      if (g_strcmp0 (fp_device_get_driver (candidate), "fpcmoh") == 0)
        {
          target = candidate;
          break;
        }
    }

  if (target == NULL)
    {
      g_printerr ("DEVICE_NOT_FOUND: no fpcmoh device was discovered.\n");
      return EXIT_FAILURE;
    }

  g_print ("DEVICE_FOUND: name=%s driver=%s enroll_stages=%d\n",
           fp_device_get_name (target),
           fp_device_get_driver (target),
           fp_device_get_nr_enroll_stages (target));

  cancellable = g_cancellable_new ();
  timeout = (ProbeTimeout) { cancellable, FALSE };
  timeout_id = g_timeout_add_seconds (PROBE_TIMEOUT_SECONDS,
                                      cancel_probe,
                                      &timeout);

  opened = fp_device_open_sync (target, cancellable, &error);

  if (!timeout.fired)
    g_source_remove (timeout_id);

  if (!opened)
    {
      g_printerr ("OPEN_FAILED: %s\n",
                  error != NULL ? error->message : "unknown error");

      if (fp_device_is_open (target))
        run_close (target);

      return EXIT_FAILURE;
    }

  g_print ("OPEN_OK\n");

  if (!run_close (target))
    return EXIT_FAILURE;

  g_print ("PROBE_OK\n");
  return EXIT_SUCCESS;
}
