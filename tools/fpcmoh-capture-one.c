/* SPDX-License-Identifier: LGPL-2.1-or-later */
/*
 * Single-image capture probe for libfprint MR !570 and FPC 10a5:9200.
 *
 * This program opens MI_00, establishes the existing TLS session, arms the
 * sensor, waits for one finger, requests one image, writes a mode-0600 PGM,
 * deactivates capture, and closes. It does not enroll, verify, replace/flush
 * keys, clear storage, access MI_01, or perform firmware operations.
 */

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <glib.h>
#include <fprint.h>

#define OPEN_CLOSE_TIMEOUT_SECONDS 30
#define CAPTURE_TIMEOUT_SECONDS 60

typedef struct
{
  GCancellable *cancellable;
  gboolean      fired;
  const gchar  *operation;
} ProbeTimeout;

static gboolean
cancel_probe (gpointer user_data)
{
  ProbeTimeout *timeout = user_data;

  timeout->fired = TRUE;
  g_printerr ("%s timeout reached; cancelling.\n", timeout->operation);
  g_cancellable_cancel (timeout->cancellable);

  return G_SOURCE_REMOVE;
}

static guint
start_timeout (ProbeTimeout *timeout,
               guint         seconds)
{
  return g_timeout_add_seconds (seconds, cancel_probe, timeout);
}

static void
stop_timeout (ProbeTimeout *timeout,
              guint         timeout_id)
{
  if (!timeout->fired)
    g_source_remove (timeout_id);
}

static gboolean
close_device (FpDevice *device)
{
  g_autoptr(GCancellable) cancellable = g_cancellable_new ();
  g_autoptr(GError) error = NULL;
  ProbeTimeout timeout = { cancellable, FALSE, "Close" };
  guint timeout_id = start_timeout (&timeout, OPEN_CLOSE_TIMEOUT_SECONDS);
  gboolean closed = fp_device_close_sync (device, cancellable, &error);

  stop_timeout (&timeout, timeout_id);

  if (!closed)
    {
      g_printerr ("CLOSE_FAILED: %s\n",
                  error != NULL ? error->message : "unknown error");
      return FALSE;
    }

  g_print ("CLOSE_OK\n");
  return TRUE;
}

static gboolean
save_pgm_exclusive (FpImage     *image,
                    const gchar *path)
{
  g_autofree gchar *checksum = NULL;
  const guchar *data;
  gsize data_len;
  guint width = fp_image_get_width (image);
  guint height = fp_image_get_height (image);
  int fd;
  FILE *stream;
  gboolean write_ok = TRUE;

  data = fp_image_get_data (image, &data_len);
  if (data == NULL || data_len != (gsize) width * height)
    {
      g_printerr ("IMAGE_INVALID: width=%u height=%u bytes=%zu\n",
                  width, height, data_len);
      return FALSE;
    }

  fd = open (path, O_WRONLY | O_CREAT | O_EXCL, 0600);
  if (fd < 0)
    {
      g_printerr ("OUTPUT_OPEN_FAILED: %s: %s\n", path, g_strerror (errno));
      return FALSE;
    }

  if (fcntl (fd, F_SETFD, FD_CLOEXEC) < 0)
    {
      g_printerr ("OUTPUT_CLOEXEC_FAILED: %s\n", g_strerror (errno));
      close (fd);
      unlink (path);
      return FALSE;
    }

  stream = fdopen (fd, "wb");
  if (stream == NULL)
    {
      g_printerr ("OUTPUT_STREAM_FAILED: %s\n", g_strerror (errno));
      close (fd);
      return FALSE;
    }

  if (fprintf (stream, "P5\n%u %u\n255\n", width, height) < 0)
    write_ok = FALSE;
  if (write_ok && fwrite (data, 1, data_len, stream) != data_len)
    write_ok = FALSE;
  if (fclose (stream) != 0)
    write_ok = FALSE;

  if (!write_ok)
    {
      g_printerr ("OUTPUT_WRITE_FAILED: %s\n", g_strerror (errno));
      unlink (path);
      return FALSE;
    }

  checksum = g_compute_checksum_for_data (G_CHECKSUM_SHA256, data, data_len);
  g_print ("IMAGE_OK: width=%u height=%u bytes=%zu sha256=%s path=%s\n",
           width, height, data_len, checksum, path);
  return TRUE;
}

int
main (int argc, char **argv)
{
  g_autoptr(FpContext) context = NULL;
  g_autoptr(GCancellable) cancellable = NULL;
  g_autoptr(GError) error = NULL;
  g_autoptr(FpImage) image = NULL;
  GPtrArray *devices;
  FpDevice *target = NULL;
  ProbeTimeout timeout;
  guint timeout_id;
  gboolean opened;
  gboolean saved;
  const gchar *output_path = "/tmp/fpcmoh-capture-001.pgm";

  if (argc > 2)
    {
      g_printerr ("Usage: %s [output.pgm]\n", argv[0]);
      return EXIT_FAILURE;
    }
  if (argc == 2)
    output_path = argv[1];

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

  if (!fp_device_has_feature (target, FP_DEVICE_FEATURE_CAPTURE))
    {
      g_printerr ("CAPTURE_UNSUPPORTED\n");
      return EXIT_FAILURE;
    }

  g_print ("DEVICE_FOUND: name=%s driver=%s\n",
           fp_device_get_name (target), fp_device_get_driver (target));

  cancellable = g_cancellable_new ();
  timeout = (ProbeTimeout) { cancellable, FALSE, "Open" };
  timeout_id = start_timeout (&timeout, OPEN_CLOSE_TIMEOUT_SECONDS);
  opened = fp_device_open_sync (target, cancellable, &error);
  stop_timeout (&timeout, timeout_id);

  if (!opened)
    {
      g_printerr ("OPEN_FAILED: %s\n",
                  error != NULL ? error->message : "unknown error");
      return EXIT_FAILURE;
    }

  g_print ("OPEN_OK\nPLACE_ONE_FINGER_ON_SENSOR\n");

  g_clear_object (&cancellable);
  g_clear_error (&error);
  cancellable = g_cancellable_new ();
  timeout = (ProbeTimeout) { cancellable, FALSE, "Capture" };
  timeout_id = start_timeout (&timeout, CAPTURE_TIMEOUT_SECONDS);
  image = fp_device_capture_sync (target, TRUE, cancellable, &error);
  stop_timeout (&timeout, timeout_id);

  if (image == NULL)
    {
      g_printerr ("CAPTURE_FAILED: %s\n",
                  error != NULL ? error->message : "unknown error");
      close_device (target);
      return EXIT_FAILURE;
    }

  saved = save_pgm_exclusive (image, output_path);
  if (!close_device (target) || !saved)
    return EXIT_FAILURE;

  g_print ("CAPTURE_OK\n");
  return EXIT_SUCCESS;
}
