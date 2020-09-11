Disturbance Storm Time analysis from OMNI data
==============================================

This section contains notebooks for the analysis of 
Disturbance Storm Time (DST) index using OMNI data. **COPY/PASTE FROM WIKIPEDIA TO BE MODIFIED**
The DST index is widely used in the context of space weather and 
gives information about the strength of the ring current around Earth caused by solar protons and electrons.
The ring current around Earth produces a magnetic field that is directly opposite Earth's magnetic field, i.e. if the difference between solar electrons and protons gets higher, then Earth's magnetic field becomes weaker. A negative Dst value means that Earth's magnetic field is weakened. This is particularly the case during solar storms. 

The two notebooks download time series data from OMNI:

-  The `First notebook <./omni_dst_forecast.ipynb>`__ trains several models to 
   forecast the DST index and evaluates their performance.
-  The `Second notebook <./omni_dst_from_other_variables.ipynb>`__ analyses the influence of each variable
   on the DST index by computing correlations and selecting the best features.


