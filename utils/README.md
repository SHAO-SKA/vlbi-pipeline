# Utils for vlbi-pipeline

## Download Astrogeo UV data

Make sure there is `source_list.txt` file in current directory, which include all the sources you want to download.


Type `bash shao_download_Astrogeo_data.sh` , all files will save to current directory.


## Download MOJAVE fits file

Type the following command to download MOJAVE fits file:

```bash
$ shao_download_MOJAVE_data.sh source_name
# for example
$ shao_download_MOJAVE_data.sh 1156+295
```