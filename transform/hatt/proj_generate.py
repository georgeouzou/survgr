
def proj_text(phi_0, lambda_0):
    return '''+proj=aeqd +lat_0=%f +lon_0=%f 
              +x_0=0 +y_0=0 +ellps=bessel +pm=athens 
              +towgs84=456.387,372.620,496.818 +units=m +no_defs
            ''' % (phi_0, lambda_0)