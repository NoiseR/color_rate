@ECHO OFF
chcp 65001 >nul

rem size: kids, XS, S, M, L, XL, XXL, XXXL
rem color: black, white, color
python color_rate.py "C:\GTX Graphics Lab\nw.exe" "Z:\test картинки\1.png" XL  white
rem                  path_to_gtx_exe              path_to_image           size color