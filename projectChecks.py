import apiData as ad


#' @title _raw has img, meta, and log
#' @description Checks the number of zip/tif images, meta files and log files in the _raw directory
def raw_img_meta_log (drive) :
  files = ad.getFiles(drive)
  
  zips = list.files(dir, pattern="zip$")
  tifs = list.files(dir, pattern="tif$")
  mets = list.files(dir, pattern="meta.*?txt$")
  logs = list.files(dir, pattern="log.*?txt$")
  
  n_zips = length(zips)
  n_tifs = length(tifs)
  n_mets = length(mets)
  n_logs = length(logs)
  
  n_imgs = n_tifs + n_zips
  
  return(list(
    test=are_equal(n_imgs, n_mets, n_logs),
    message=n_tifs + " tif + " + n_zips + " zip, " + n_mets + "meta, " + n_logs + " log"
  ))

