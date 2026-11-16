#include "itkDCMTKImageIO.h"
#include "itkGDCMImageIO.h"
#include "itkImage.h"
#include "itkImageFileReader.h"
#include <iostream>
#include <string_view>

int main(int argc, char ** argv)
{
  if (argc != 3)
  {
    std::cerr << "Usage: compare-reader gdcm|gdcm-unit|dcmtk file.dcm\n";
    return 2;
  }

  using Image = itk::Image<unsigned char, 3>;
  auto reader = itk::ImageFileReader<Image>::New();
  const std::string_view mode(argv[1]);
  if (mode == "dcmtk")
  {
    reader->SetImageIO(itk::DCMTKImageIO::New());
  }
  else if (mode == "gdcm" || mode == "gdcm-unit")
  {
    auto io = itk::GDCMImageIO::New();
    if (mode == "gdcm-unit")
    {
      io->SetSingleBitForegroundValue(1);
    }
    reader->SetImageIO(io);
  }
  else
  {
    std::cerr << "Unrecognized reader: " << mode << '\n';
    return 2;
  }

  reader->SetFileName(argv[2]);
  try
  {
    reader->Update();
  }
  catch (const itk::ExceptionObject & error)
  {
    std::cerr << error << '\n';
    return 1;
  }
  const auto * output = reader->GetOutput();
  const auto region = output->GetLargestPossibleRegion();
  const auto size = region.GetSize();
  std::cout << size[2] << ' ' << size[1] << ' ' << size[0] << '\n';
  for (size_t i = 0; i < region.GetNumberOfPixels(); ++i)
  {
    std::cout << static_cast<unsigned int>(output->GetBufferPointer()[i]) << ' ';
  }
  std::cout << '\n';
}
