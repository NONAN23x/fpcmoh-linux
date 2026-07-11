/* SPDX-License-Identifier: LGPL-2.1-or-later */
/* Offline score matrix for P5/8-bit PGM captures using MR !570 SIGFM. */

#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include "sigfm.h"

namespace
{
struct Image
{
  std::string name;
  int width;
  int height;
  std::vector<unsigned char> pixels;
};

std::string
next_token (std::istream& input)
{
  std::string token;

  while (input >> token)
    {
      if (!token.empty () && token.front () == '#')
        {
          input.ignore (std::numeric_limits<std::streamsize>::max (), '\n');
          continue;
        }
      return token;
    }

  throw std::runtime_error ("unexpected end of PGM header");
}

Image
read_pgm (const std::string& path)
{
  std::ifstream input (path, std::ios::binary);
  Image image;
  int max_value;

  if (!input)
    throw std::runtime_error ("cannot open " + path);

  if (next_token (input) != "P5")
    throw std::runtime_error (path + " is not a binary P5 PGM");

  image.width = std::stoi (next_token (input));
  image.height = std::stoi (next_token (input));
  max_value = std::stoi (next_token (input));

  if (image.width <= 0 || image.height <= 0 || max_value != 255)
    throw std::runtime_error (path + " has unsupported PGM geometry/depth");

  char separator;
  if (!input.get (separator) || separator != '\n')
    throw std::runtime_error (path + " has an invalid PGM header separator");

  const auto pixel_count = static_cast<std::size_t> (image.width) *
                           static_cast<std::size_t> (image.height);
  image.pixels.resize (pixel_count);
  input.read (reinterpret_cast<char *> (image.pixels.data ()),
              static_cast<std::streamsize> (pixel_count));

  if (input.gcount () != static_cast<std::streamsize> (pixel_count))
    throw std::runtime_error (path + " has a truncated pixel payload");

  if (input.peek () != std::char_traits<char>::eof ())
    throw std::runtime_error (path + " has trailing bytes after its pixel payload");

  image.name = std::filesystem::path (path).filename ().string ();
  return image;
}

using SigfmInfo = std::unique_ptr<SigfmImgInfo, decltype (&sigfm_free_info)>;
}

int
main (int argc, char **argv)
{
  if (argc < 3)
    {
      std::cerr << "Usage: " << argv[0] << " image1.pgm image2.pgm [...]\n";
      return EXIT_FAILURE;
    }

  try
    {
      std::vector<Image> images;
      std::vector<SigfmInfo> infos;

      images.reserve (static_cast<std::size_t> (argc - 1));
      infos.reserve (static_cast<std::size_t> (argc - 1));

      for (int i = 1; i < argc; i++)
        {
          images.push_back (read_pgm (argv[i]));
          const Image& image = images.back ();
          SigfmInfo info (sigfm_extract (image.pixels.data (),
                                        image.width,
                                        image.height),
                          sigfm_free_info);

          if (!info)
            throw std::runtime_error (image.name + " feature extraction failed");

          std::cout << "SAMPLE " << image.name
                    << " keypoints=" << sigfm_keypoints_count (info.get ())
                    << " geometry=" << image.width << 'x' << image.height
                    << '\n';
          infos.push_back (std::move (info));
        }

      for (std::size_t frame = 0; frame < infos.size (); frame++)
        for (std::size_t enrolled = 0; enrolled < infos.size (); enrolled++)
          {
            const int score = sigfm_match_score (infos[frame].get (),
                                                 infos[enrolled].get ());
            std::cout << "SCORE frame=" << images[frame].name
                      << " enrolled=" << images[enrolled].name
                      << " score=" << score
                      << " threshold=10 verdict="
                      << (score >= 10 ? "ACCEPT" : "REJECT") << '\n';
          }
    }
  catch (const std::exception& error)
    {
      std::cerr << "ERROR: " << error.what () << '\n';
      return EXIT_FAILURE;
    }

  return EXIT_SUCCESS;
}
