
## convert pdf to gif
#for i in \
#    fit_zoom_fixPara_gaus_r0.2to1.0 \
#    fit_zoom_fixPara_gaus_r0.2to1.2 \
#    fit_zoom_fixPara_gaus_r0.2to1.4 \
#    fit_zoom_fixPara_gaus_r0.3to1.1 \
#    fit_zoom_fixPara_gaus_r0.3to1.3 \
#    fit_zoom_fixPara_gaus_r0.3to1.5 \
#    fit_zoom_fixPara_gaus_r0.4to1.2 \
#    fit_zoom_fixPara_gaus_r0.4to1.4 \
#    fit_zoom_fixPara_gaus_r0.4to1.6
#do
#    convert ${i}.pdf ${i}.gif
#done

## create animated gif
convert -delay 200 \
    fit_zoom_fixPara_gaus_r0.2to1.0.gif \
    fit_zoom_fixPara_gaus_r0.2to1.2.gif \
    fit_zoom_fixPara_gaus_r0.2to1.4.gif \
    fit_zoom_fixPara_gaus_r0.3to1.1.gif \
    fit_zoom_fixPara_gaus_r0.3to1.3.gif \
    fit_zoom_fixPara_gaus_r0.3to1.5.gif \
    fit_zoom_fixPara_gaus_r0.4to1.2.gif \
    fit_zoom_fixPara_gaus_r0.4to1.4.gif \
    fit_zoom_fixPara_gaus_r0.4to1.6.gif \
    -loop 0 \
    play_fitPara_gaus.gif

## clear up the individual gif
#rm -rf fit*gif

#echo done
