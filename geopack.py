import numpy as np
import t89
import t96
import t01
import t04


def igrf_gsm(xgsm,ygsm,zgsm):
    """
    Calculates components of the main (internal) geomagnetic field in the geocentric solar
    magnetospheric coordinate system, using IAGA international geomagnetic reference model
    coefficients (e.g., http://www.ngdc.noaa.gov/iaga/vmod/igrf.html revised: 22 march, 2005)

    Before the first call of this subroutine, or if the date/time (iyear,iday,ihour,min,isec)
    was changed, the model coefficients and GEO-GSM rotation matrix elements should be updated
    by calling the subroutine recalc

    Python version by Sheng Tian

    :param xgsm,ygsm,zgsm: cartesian GSM coordinates (in units Re=6371.2 km)
    :return: hxgsm,hygsm,hzgsm. Cartesian GSM components of the main geomagnetic field in nanotesla
    """


    # common /geopack2/ g(105),h(105),rec(105)
    global g, h, rec

    xgeo,ygeo,zgeo = geogsm(xgsm,ygsm,zgsm,-1)

    rho2 = xgeo**2+ygeo**2
    r = np.sqrt(rho2+zgeo**2)
    c = zgeo/r
    rho = np.sqrt(rho2)
    s = rho/r
    if s < 1e-5:
        cf,sf = [1.,0]
    else:
        cf = xgeo/rho
        sf = ygeo/rho

    pp = 1./r
    p = pp

    # In this new version, the optimal value of the parameter nm (maximal order of the spherical
    # harmonic expansion) is not user-prescribed, but calculated inside the subroutine, based
    #  on the value of the radial distance r:
    irp3 = np.int64(r+2)
    nm = np.int64(3+30/irp3)
    if nm > 13: nm = 13

    k = nm+1
    a = np.empty(14)
    b = np.empty(14)
    for n in range(k):
        p = p*pp
        a[n]=p
        b[n]=p*(n+1)

    p,d, bbr,bbt,bbf = [1.,0, 0,0,0]
    for m in range(1,k+1):
        if m == 1: x,y = [0.,1]
        else:
            mm=m-1
            w=x
            x=w*cf+y*sf
            y=y*cf-w*sf
        q,z,bi,p2,d2 = [p,d,0.,0,0]
        for n in range(m,k+1):
            an=a[n-1]
            mn=np.int64(n*(n-1)/2+m)
            e=g[mn-1]
            hh=h[mn-1]
            w=e*y+hh*x
            bbr=bbr+b[n-1]*w*q
            bbt=bbt-an*w*z
            if m != 1:
                qq=q
                if s < 1.e-5: qq=z
                bi=bi+an*(e*x-hh*y)*qq
            xk=rec[mn-1]
            dp=c*z-s*q-xk*d2
            pm=c*q-xk*p2
            d2,p2,z = [z,q,dp]
            q=pm

        d=s*d+c*p
        p=s*p
        if m == 1: continue
        else:
            bi=bi*mm
            bbf=bbf+bi

    br=bbr
    bt=bbt
    if s < 1.e-5:
        if c< 0.: bbf=-bbf
        bf=bbf
    else: bf = bbf/s

    he=br*s+bt*c
    hxgeo=he*cf-bf*sf
    hygeo=he*sf+bf*cf
    hzgeo=br*c-bt*s

    return geogsm(hxgeo,hygeo,hzgeo,1)

def igrf_geo(r,theta,phi):
    """
    Calculates components of the main (internal) geomagnetic field in the spherical geographic
    (geocentric) coordinate system, using IAGA international geomagnetic reference model
    coefficients  (e.g., http://www.ngdc.noaa.gov/iaga/vmod/igrf.html, revised: 22 march, 2005)

    Before the first call of this subroutine, or if the date (iyear and iday) was changed,
    the model coefficients should be updated by calling the subroutine recalc

    Python version by Sheng Tian

    :param r: spherical geographic (geocentric) coordinates: radial distance r in units Re=6371.2 km
    :param theta: colatitude theta in radians
    :param phi: longitude phi in radians
    :return: br, btheta, bphi. Spherical components of the main geomagnetic field in nanotesla
        (positive br outward, btheta southward, bphi eastward)
    """


    # common /geopack2/ g(105),h(105),rec(105)
    global g, h, rec

    ct = np.cos(theta)
    st = np.sin(theta)
    minst = 1e-5
    if np.abs(st) < minst: smlst = True
    else: smlst = False

    # In this new version, the optimal value of the parameter nm (maximal order of the spherical
    # harmonic expansion) is not user-prescribed, but calculated inside the subroutine, based
    # on the value of the radial distance r:
    irp3 = np.int64(r+2)
    nm = np.int64(3+30/irp3)
    if nm > 13: nm = 13
    k = nm+1

    a = np.empty(k)
    b = np.empty(k)
    ar = 1/r        # a/r
    a[0] = ar*ar    # a[n] = (a/r)^(n+2).
    b[0] = a[0]     # b[n] = (n+1)(a/r)^(n+2)
    for n in range(1,k):
        a[n] = a[n-1]*ar
        b[n] = a[n]*(n+1)


    br,bt,bf = [0.]*3
    d,p = [0.,1]

    # m = 0. P_n,0
    m = 0
    smf,cmf = [0.,1]
    p1,d1,p2,d2 = [p,d,0.,0]
    l0 = 0
    mn = l0
    for n in range(m,k):
        w = g[mn]*cmf+h[mn]*smf
        br += b[n]*w*p1          # p1 is P_m,n.
        bt -= a[n]*w*d1          # d1 is dP_m,n/dt.
        xk = rec[mn]
        d0 = ct*d1-st*p1-xk*d2   # dP_m,n/dt = ct*(2n-1)/(n-m)*dP_m,n-1/dt - st*(2n-1)/(n-m)*P_m,n-1 - (n+m-1)/(n-m)*dP_m,n-2/dt
        p0 = ct*p1-xk*p2         # P_m,n = ct*(2n-1)/(n-m)*P_m,n-1 - (n+m-1)/(n-m)*P_m,n-2
        d2,p2,d1 = [d1,p1,d0]
        p1 = p0
        mn += n+1
    d = st*d+ct*p   # dP_m,m/dt
    p = st*p        # P_m,m

    # P_mn
    l0 = 0
    for m in range(1,k):        # sum over m
        smf = np.sin(m*phi)     # sin(m*phi)
        cmf = np.cos(m*phi)     # cos(m*phi)
        p1,d1,p2,d2 = [p,d,0.,0]
        tbf = 0.
        l0 += m+1
        mn = l0
        for n in range(m,k):    # sum over n
            w=g[mn]*cmf+h[mn]*smf   # [g_mn*cos(m*phi)+h_mn*sin(m*phi)]
            br += b[n]*w*p1
            bt -= a[n]*w*d1
            tp = p1
            if smlst: tp = d1
            tbf += a[n]*(g[mn]*smf-h[mn]*cmf)*tp
            xk = rec[mn]
            d0 = ct*d1-st*p1-xk*d2  # dP_m,n/dt = ct*(2n-1)/(n-m)*dP_m,n-1/dt - st*(2n-1)/(n-m)*P_m,n-1 - (n+m-1)/(n-m)*dP_m,n-2/dt
            p0 = ct*p1-xk*p2        # P_m,n = ct*(2n-1)/(n-m)*P_m,n-1 - (n+m-1)/(n-m)*P_m,n-2
            d2,p2,d1 = [d1,p1,d0]
            p1=p0
            mn += n+1

        d = st*d+ct*p    # dP_m,m/dt
        p = st*p         # P_m,m
        tbf *= m
        bf += tbf

    if smlst:
        if ct < 0.: bf = -bf
    else: bf /= st

    return br,bt,bf


def dip(xgsm,ygsm,zgsm):
    """
    Calculates gsm components of a geodipole field with the dipole moment
    corresponding to the epoch, specified by calling subroutine recalc (should be
    invoked before the first use of this one and in case the date/time was changed).

    :param xgsm,ygsm,zgsm: GSM coordinates in Re (1 Re = 6371.2 km)
    :return: bxgsm,bygsm,gzgsm. Field components in gsm system, in nanotesla.

    Last modification: May 4, 2005.
    Author: N. A. Tsyganenko
    """

    # common /geopack1/ aaa(10),sps,cps,bbb(23)
    # common /geopack2/ g(105),h(105),rec(105)
    global aaa, sps,cps, bbb, g, h, rec

    dipmom = np.sqrt(g[1]**2+g[2]**2+h[2]**2)

    p = xgsm**2
    u = zgsm**2
    v = 3.*zgsm*xgsm
    t = ygsm**2
    q = dipmom/np.sqrt(p+t+u)**5

    bxgsm = q*((t+u-2.*p)*sps-v*cps)
    bygsm = -3.*ygsm*q*(xgsm*sps+zgsm*cps)
    bzgsm = q*((p+t-2.*u)*cps-v*sps)

    return bxgsm,bygsm,bzgsm



def recalc(iyear,iday,ihour,min,isec):
    """
    1. Prepares elements of rotation matrices for transformations of vectors between
        several coordinate systems, most frequently used in space physics.
    2. Prepares coefficients used in the calculation of the main geomagnetic field (igrf model)

    This subroutine should be invoked before using the following subroutines:
        igrf_geo, igrf_gsm, dip, geomag, geogsm, magsm, smgsm, gsmgse, geigeo.
    There is no need to repeatedly invoke recalc, if multiple calculations are made for the same date and time.

    :param iyear: year number (four digits)
    :param iday: day of year (day 1 = Jan 1)
    :param ihour: hour of day (00 to 23)
    :param min: minute of hour (00 to 59)
    :param isec: seconds of minute (00 to 59)
    :return: none (all output quantities are placed into the common blocks /geopack1/ and /geopack2/)


    Author:  N.A. Tsyganenko
    Date:    Dec.1, 1991
    Python version by Sheng Tian

    Correction of May 9, 2006:  interpolation of the coefficients (between
        labels 50 and 105) is now made through the last element of the arrays
        g(105) and h(105) (previously made only through n=66, which in some
        cases caused runtime errors)

    Revision of May 3, 2005:
        The table of IGRF coefficients was extended to include those for the epoch 2005
        the maximal order of spherical harmonics was also increased up to 13
        (for details, see http://www.ngdc.noaa.gov/iaga/vmod/igrf.html)

    Revision of April 3, 2003:
        The code now includes preparation of the model coefficients for the subroutines
        IGRF and geomag. this eliminates the need for the save statements, used in the
        old versions, making the codes easier and more compiler-independent.
    """


    # The common block /geopack1/ contains elements of the rotation matrices and other
    # parameters related to the coordinate transformations performed by this package
    # common /geopack1/ st0,ct0,sl0,cl0,ctcl,stcl,ctsl,stsl,sfi,cfi,sps,
    # cps,shi,chi,hi,psi,xmut,a11,a21,a31,a12,a22,a32,a13,a23,a33,ds3,
    # cgst,sgst,ba(6)

    # st0/ct0 - sin/cos of teta0 (colat in geo?). sl0/cl0 - sin/cos of lambda0 (longitude in geo?).
    # ctcl/stcl - . ctsl/stsl - . geo x and z?
    # sfi/cfi/xmut - rotate angle between mag and sm and its sin/cos.
    # sps/cps/psi - tilt angle and its sin/cos.
    # shi/chi/hi - rotate angle between gse to gsm and its sin/cos.
    # a[11,...,33] - matrix converts geo to gsm.
    # cgst/sgst - cos/sin of gst.
    # ds3.
    # ba(6).
    global st0,ct0,sl0,cl0,ctcl,stcl,ctsl,stsl,sfi,cfi,sps,cps, \
        shi,chi,hi,psi,xmut,a11,a21,a31,a12,a22,a32,a13,a23,a33,ds3,cgst,sgst,ba

    # The common block /geopack2/ contains coefficients of the IGRF field model, calculated
    # for a given year and day from their standard epoch values. the array rec contains
    # coefficients used in the recursion relations for legendre associate polynomials.
    # common /geopack2/ g(105),h(105),rec(105)
    global g,h,rec

    # TODO: use the igrf coeff directly.
    g65 = np.array([0.,-30334.,-2119.,-1662.,2997.,1594.,1297.,-2038.,1292.,
        856.,957.,804.,479.,-390.,252.,-219.,358.,254.,-31.,-157.,-62.,
        45.,61.,8.,-228.,4.,1.,-111.,75.,-57.,4.,13.,-26.,-6.,13.,1.,13.,
        5.,-4.,-14.,0.,8.,-1.,11.,4.,8.,10.,2.,-13.,10.,-1.,-1.,5.,1.,-2.,
        -2.,-3.,2.,-5.,-2.,4.,4.,0.,2.,2.,0.]+39*[0.])
    h65 = np.array([0.,0.,5776.,0.,-2016.,114.,0.,-404.,240.,-165.,0.,148.,
        -269.,13.,-269.,0.,19.,128.,-126.,-97.,81.,0.,-11.,100.,68.,-32.,
        -8.,-7.,0.,-61.,-27.,-2.,6.,26.,-23.,-12.,0.,7.,-12.,9.,-16.,4.,
        24.,-3.,-17.,0.,-22.,15.,7.,-4.,-5.,10.,10.,-4.,1.,0.,2.,1.,2.,
        6.,-4.,0.,-2.,3.,0.,-6.]+39*[0.])
    g70 = np.array([0.,-30220.,-2068.,-1781.,3000.,1611.,1287.,-2091.,1278.,
        838.,952.,800.,461.,-395.,234.,-216.,359.,262.,-42.,-160.,-56.,
        43.,64.,15.,-212.,2.,3.,-112.,72.,-57.,1.,14.,-22.,-2.,13.,-2.,
        14.,6.,-2.,-13.,-3.,5.,0.,11.,3.,8.,10.,2.,-12.,10.,-1.,0.,3.,
        1.,-1.,-3.,-3.,2.,-5.,-1.,6.,4.,1.,0.,3.,-1.]+39*[0.])
    h70 = np.array([0.,0.,5737.,0.,-2047.,25.,0.,-366.,251.,-196.,0.,167.,
        -266.,26.,-279.,0.,26.,139.,-139.,-91.,83.,0.,-12.,100.,72.,-37.,
        -6.,1.,0.,-70.,-27.,-4.,8.,23.,-23.,-11.,0.,7.,-15.,6.,-17.,6.,
        21.,-6.,-16.,0.,-21.,16.,6.,-4.,-5.,10.,11.,-2.,1.,0.,1.,1.,3.,
        4.,-4.,0.,-1.,3.,1.,-4.]+39*[0.])
    g75 = np.array([0.,-30100.,-2013.,-1902.,3010.,1632.,1276.,-2144.,1260.,
        830.,946.,791.,438.,-405.,216.,-218.,356.,264.,-59.,-159.,-49.,
        45.,66.,28.,-198.,1.,6.,-111.,71.,-56.,1.,16.,-14.,0.,12.,-5.,
        14.,6.,-1.,-12.,-8.,4.,0.,10.,1.,7.,10.,2.,-12.,10.,-1.,-1.,4.,
        1.,-2.,-3.,-3.,2.,-5.,-2.,5.,4.,1.,0.,3.,-1.]+39*[0.])
    h75 = np.array([0.,0.,5675.,0.,-2067.,-68.,0.,-333.,262.,-223.,0.,191.,
        -265.,39.,-288.,0.,31.,148.,-152.,-83.,88.,0.,-13.,99.,75.,-41.,
        -4.,11.,0.,-77.,-26.,-5.,10.,22.,-23.,-12.,0.,6.,-16.,4.,-19.,6.,
        18.,-10.,-17.,0.,-21.,16.,7.,-4.,-5.,10.,11.,-3.,1.,0.,1.,1.,3.,
        4.,-4.,-1.,-1.,3.,1.,-5.]+39*[0.])
    g80 = np.array([0.,-29992.,-1956.,-1997.,3027.,1663.,1281.,-2180.,1251.,
        833.,938.,782.,398.,-419.,199.,-218.,357.,261.,-74.,-162.,-48.,
        48.,66.,42.,-192.,4.,14.,-108.,72.,-59.,2.,21.,-12.,1.,11.,-2.,
        18.,6.,0.,-11.,-7.,4.,3.,6.,-1.,5.,10.,1.,-12.,9.,-3.,-1.,7.,2.,
        -5.,-4.,-4.,2.,-5.,-2.,5.,3.,1.,2.,3.,0.]+39*[0.])
    h80 = np.array([0.,0.,5604.,0.,-2129.,-200.,0.,-336.,271.,-252.,0.,212.,
        -257.,53.,-297.,0.,46.,150.,-151.,-78.,92.,0.,-15.,93.,71.,-43.,
        -2.,17.,0.,-82.,-27.,-5.,16.,18.,-23.,-10.,0.,7.,-18.,4.,-22.,9.,
        16.,-13.,-15.,0.,-21.,16.,9.,-5.,-6.,9.,10.,-6.,2.,0.,1.,0.,3.,
        6.,-4.,0.,-1.,4.,0.,-6.]+39*[0.])
    g85 = np.array([0.,-29873.,-1905.,-2072.,3044.,1687.,1296.,-2208.,1247.,
        829.,936.,780.,361.,-424.,170.,-214.,355.,253.,-93.,-164.,-46.,
        53.,65.,51.,-185.,4.,16.,-102.,74.,-62.,3.,24.,-6.,4.,10.,0.,21.,
        6.,0.,-11.,-9.,4.,4.,4.,-4.,5.,10.,1.,-12.,9.,-3.,-1.,7.,1.,-5.,
        -4.,-4.,3.,-5.,-2.,5.,3.,1.,2.,3.,0.]+39*[0.])
    h85 = np.array([0.,0.,5500.,0.,-2197.,-306.,0.,-310.,284.,-297.,0.,232.,
        -249.,69.,-297.,0.,47.,150.,-154.,-75.,95.,0.,-16.,88.,69.,-48.,
        -1.,21.,0.,-83.,-27.,-2.,20.,17.,-23.,-7.,0.,8.,-19.,5.,-23.,11.,
        14.,-15.,-11.,0.,-21.,15.,9.,-6.,-6.,9.,9.,-7.,2.,0.,1.,0.,3.,
        6.,-4.,0.,-1.,4.,0.,-6.]+39*[0.])
    g90 = np.array([
              0., -29775.,  -1848.,  -2131.,   3059.,   1686.,   1314.,
          -2239.,   1248.,    802.,    939.,    780.,    325.,   -423.,
            141.,   -214.,    353.,    245.,   -109.,   -165.,    -36.,
             61.,     65.,     59.,   -178.,      3.,     18.,    -96.,
             77.,    -64.,      2.,     26.,     -1.,      5.,      9.,
              0.,     23.,      5.,     -1.,    -10.,    -12.,      3.,
              4.,      2.,     -6.,      4.,      9.,      1.,    -12.,
              9.,     -4.,     -2.,      7.,      1.,     -6.,     -3.,
             -4.,      2.,     -5.,     -2.,      4.,      3.,      1.,
              3.,      3.,      0.]+  39*[0.])
    h90 = np.array([
             0.,      0.,   5406.,      0.,  -2279.,   -373.,      0.,
          -284.,    293.,   -352.,      0.,    247.,   -240.,     84.,
          -299.,      0.,     46.,    154.,   -153.,    -69.,     97.,
             0.,    -16.,     82.,     69.,    -52.,      1.,     24.,
             0.,    -80.,    -26.,      0.,     21.,     17.,    -23.,
            -4.,      0.,     10.,    -19.,      6.,    -22.,     12.,
            12.,    -16.,    -10.,      0.,    -20.,     15.,     11.,
            -7.,     -7.,      9.,      8.,     -7.,      2.,      0.,
             2.,      1.,      3.,      6.,     -4.,      0.,     -2.,
             3.,     -1.,     -6.]+   39*[0.])
    g95 = np.array([
             0., -29692.,  -1784.,  -2200.,   3070.,   1681.,   1335.,
         -2267.,   1249.,    759.,    940.,    780.,    290.,   -418.,
           122.,   -214.,    352.,    235.,   -118.,   -166.,    -17.,
            68.,     67.,     68.,   -170.,     -1.,     19.,    -93.,
            77.,    -72.,      1.,     28.,      5.,      4.,      8.,
            -2.,     25.,      6.,     -6.,     -9.,    -14.,      9.,
             6.,     -5.,     -7.,      4.,      9.,      3.,    -10.,
             8.,     -8.,     -1.,     10.,     -2.,     -8.,     -3.,
            -6.,      2.,     -4.,     -1.,      4.,      2.,      2.,
             5.,      1.,      0.]+    39*[0.])
    h95 = np.array([
             0.,      0.,   5306.,      0.,  -2366.,   -413.,      0.,
          -262.,    302.,   -427.,      0.,    262.,   -236.,     97.,
          -306.,      0.,     46.,    165.,   -143.,    -55.,    107.,
             0.,    -17.,     72.,     67.,    -58.,      1.,     36.,
             0.,    -69.,    -25.,      4.,     24.,     17.,    -24.,
            -6.,      0.,     11.,    -21.,      8.,    -23.,     15.,
            11.,    -16.,     -4.,      0.,    -20.,     15.,     12.,
            -6.,     -8.,      8.,      5.,     -8.,      3.,      0.,
             1.,      0.,      4.,      5.,     -5.,     -1.,     -2.,
             1.,     -2.,     -7.]+    39*[0.])
    g00 = np.array([
             0.,-29619.4, -1728.2, -2267.7,  3068.4,  1670.9,  1339.6,
         -2288.,  1252.1,   714.5,   932.3,   786.8,    250.,   -403.,
          111.3,  -218.8,   351.4,   222.3,  -130.4,  -168.6,   -12.9,
           72.3,    68.2,    74.2,  -160.9,    -5.9,    16.9,   -90.4,
           79.0,   -74.0,      0.,    33.3,     9.1,     6.9,     7.3,
           -1.2,    24.4,     6.6,    -9.2,    -7.9,   -16.6,     9.1,
            7.0,    -7.9,     -7.,      5.,     9.4,      3.,   - 8.4,
            6.3,    -8.9,    -1.5,     9.3,    -4.3,    -8.2,    -2.6,
            -6.,     1.7,    -3.1,    -0.5,     3.7,      1.,      2.,
            4.2,     0.3,    -1.1,     2.7,    -1.7,    -1.9,     1.5,
           -0.1,     0.1,    -0.7,     0.7,     1.7,     0.1,     1.2,
            4.0,    -2.2,    -0.3,     0.2,     0.9,    -0.2,     0.9,
           -0.5,     0.3,    -0.3,    -0.4,    -0.1,    -0.2,    -0.4,
           -0.2,    -0.9,     0.3,     0.1,    -0.4,     1.3,    -0.4,
            0.7,    -0.4,     0.3,    -0.1,     0.4,      0.,     0.1])
    h00 = np.array([
             0.,      0.,  5186.1,      0., -2481.6,  -458.0,      0.,
         -227.6,   293.4,  -491.1,      0.,   272.6,  -231.9,   119.8,
         -303.8,      0.,    43.8,   171.9,  -133.1,   -39.3,   106.3,
             0.,   -17.4,    63.7,    65.1,   -61.2,     0.7,    43.8,
             0.,   -64.6,   -24.2,     6.2,     24.,    14.8,   -25.4,
           -5.8,     0.0,    11.9,   -21.5,     8.5,   -21.5,    15.5,
            8.9,   -14.9,    -2.1,     0.0,   -19.7,    13.4,    12.5,
           -6.2,    -8.4,     8.4,     3.8,    -8.2,     4.8,     0.0,
            1.7,     0.0,     4.0,     4.9,    -5.9,    -1.2,    -2.9,
            0.2,    -2.2,    -7.4,     0.0,     0.1,     1.3,    -0.9,
           -2.6,     0.9,    -0.7,    -2.8,    -0.9,    -1.2,    -1.9,
           -0.9,     0.0,    -0.4,     0.3,     2.5,    -2.6,     0.7,
            0.3,     0.0,     0.0,     0.3,    -0.9,    -0.4,     0.8,
            0.0,    -0.9,     0.2,     1.8,    -0.4,    -1.0,    -0.1,
            0.7,     0.3,     0.6,     0.3,    -0.2,    -0.5,    -0.9])
    g05 = np.array([
             0.,-29556.8, -1671.8, -2340.5,   3047.,  1656.9,  1335.7,
        -2305.3,  1246.8,   674.4,   919.8,   798.2,   211.5,  -379.5,
          100.2,  -227.6,   354.4,   208.8,  -136.6,  -168.3,   -14.1,
           72.9,    69.6,    76.6,  -151.1,   -15.0,    14.7,   -86.4,
           79.8,   -74.4,    -1.4,    38.6,    12.3,     9.4,     5.5,
            2.0,    24.8,     7.7,   -11.4,    -6.8,   -18.0,    10.0,
            9.4,   -11.4,    -5.0,     5.6,     9.8,     3.6,    -7.0,
            5.0,   -10.8,    -1.3,     8.7,    -6.7,    -9.2,    -2.2,
           -6.3,     1.6,    -2.5,    -0.1,     3.0,     0.3,     2.1,
            3.9,    -0.1,    -2.2,     2.9,    -1.6,    -1.7,     1.5,
           -0.2,     0.2,    -0.7,     0.5,     1.8,     0.1,     1.0,
            4.1,    -2.2,    -0.3,     0.3,     0.9,    -0.4,     1.0,
           -0.4,     0.5,    -0.3,    -0.4,     0.0,    -0.4,     0.0,
           -0.2,    -0.9,     0.3,     0.3,    -0.4,     1.2,    -0.4,
            0.7,    -0.3,     0.4,    -0.1,     0.4,    -0.1,    -0.3])
    h05 = np.array([
             0.,     0.0,  5080.0,     0.0, -2594.9,  -516.7,     0.0,
         -200.4,   269.3,  -524.5,     0.0,   281.4,  -225.8,   145.7,
         -304.7,     0.0,    42.7,   179.8,  -123.0,   -19.5,   103.6,
            0.0,   -20.2,    54.7,    63.7,   -63.4,     0.0,    50.3,
            0.0,   -61.4,   -22.5,     6.9,    25.4,    10.9,   -26.4,
           -4.8,     0.0,    11.2,   -21.0,     9.7,   -19.8,    16.1,
            7.7,   -12.8,    -0.1,     0.0,   -20.1,    12.9,    12.7,
           -6.7,    -8.1,     8.1,     2.9,    -7.9,     5.9,     0.0,
            2.4,     0.2,     4.4,     4.7,    -6.5,    -1.0,    -3.4,
           -0.9,    -2.3,    -8.0,     0.0,     0.3,     1.4,    -0.7,
           -2.4,     0.9,    -0.6,    -2.7,    -1.0,    -1.5,    -2.0,
           -1.4,     0.0,    -0.5,     0.3,     2.3,    -2.7,     0.6,
            0.4,     0.0,     0.0,     0.3,    -0.8,    -0.4,     1.0,
            0.0,    -0.7,     0.3,     1.7,    -0.5,    -1.0,     0.0,
            0.7,     0.2,     0.6,     0.4,    -0.2,    -0.5,    -1.0])
    dg05 = np.array([
              0.0,   8.8,    10.8,   -15.0,    -6.9,    -1.0,    -0.3,
             -3.1,  -0.9,    -6.8,    -2.5,     2.8,    -7.1,     5.9,
             -3.2,  -2.6,     0.4,    -3.0,    -1.2,     0.2,    -0.6,
             -0.8,   0.2,    -0.2,     2.1,    -2.1,    -0.4,     1.3,
             -0.4,   0.0,    -0.2,     1.1,     0.6,     0.4,    -0.5,
              0.9,  -0.2,     0.2,    -0.2,     0.2,    -0.2,     0.2,
              0.5,  -0.7,     0.5])

    dh05 = np.array([
              0.0,   0.0,   -21.3,     0.0,   -23.3,   -14.0,     0.0,
              5.4,  -6.5,    -2.0,     0.0,     2.0,     1.8,     5.6,
              0.0,   0.0,     0.1,     1.8,     2.0,     4.5,    -1.0,
              0.0,  -0.4,    -1.9,    -0.4,    -0.4,    -0.2,     0.9,
              0.0,   0.8,     0.4,     0.1,     0.2,    -0.9,    -0.3,
              0.3,   0.0,    -0.2,     0.2,     0.2,     0.4,     0.2,
             -0.3,   0.5,     0.4])


    # We are restricted by the interval 1965-2010, for which the IGRF coefficients
    # are known; if iyear is outside this interval, then the subroutine uses the
    # nearest limiting value and prints a warning:
    iy=iyear

    if iy < 1965: iy = 1965
    if iy > 2010: iy = 2010


    # Calculate the array rec, containing coefficients for the recursion relations,
    # used in the IGRF subroutine for calculating the associate legendre polynomials
    # and their derivatives:

    rec = np.empty(105,dtype=float)
    g   = np.empty(105,dtype=float)
    h   = np.empty(105,dtype=float)

    rec = np.empty(105,dtype=float)
    nn = 0
    for n in range(14):
        n2 = 2*n+1
        n2 = n2*(n2-2)      # (2n+1)(2n-1)
        for m in range(n+1):
            rec[nn] = (n-m)*(n+m)/n2    # (n-m)(n+m)/(2n+1)(2n-1)
            nn += 1



    if iy < 1970:       # interpolate between 1965 - 1970
        f2=(iy+(iday-1)/365.25-1965)/5.
        f1=1.-f2
        for n in range(105):
           g[n]=g65[n]*f1+g70[n]*f2
           h[n]=h65[n]*f1+h70[n]*f2
    elif iy < 1975:     # interpolate between 1970 - 1975
        f2=(iy+(iday-1)/365.25-1970)/5.
        f1=1.-f2
        for n in range(105):
            g[n]=g70[n]*f1+g75[n]*f2
            h[n]=h70[n]*f1+h75[n]*f2
    elif iy < 1980:     # interpolate between 1975 - 1980
        f2=(iy+(iday-1)/365.25-1975)/5.
        f1=1.-f2
        for n in range(105):
            g[n]=g75[n]*f1+g80[n]*f2
            h[n]=h75[n]*f1+h80[n]*f2
    elif iy < 1985:     # interpolate between 1980 - 1985
        f2=(iy+(iday-1)/365.25-1980)/5.
        f1=1.-f2
        for n in range(105):
            g[n]=g80[n]*f1+g85[n]*f2
            h[n]=h80[n]*f1+h85[n]*f2
    elif iy < 1990:     # interpolate between 1985 - 1990
        f2=(iy+(iday-1)/365.25-1985)/5.
        f1=1.-f2
        for n in range(105):
            g[n]=g85[n]*f1+g90[n]*f2
            h[n]=h85[n]*f1+h90[n]*f2
    elif iy < 1995:     # interpolate between 1990 - 1995
        f2=(iy+(iday-1)/365.25-1990)/5.
        f1=1.-f2
        for n in range(105):
            g[n]=g90[n]*f1+g95[n]*f2
            h[n]=h90[n]*f1+h95[n]*f2
    elif iy < 2000:     # interpolate between 1995 - 2000
        f2=(iy+(iday-1)/365.25-1995)/5.
        f1=1.-f2
        for n in range(105):
            g[n]=g95[n]*f1+g00[n]*f2
            h[n]=h95[n]*f1+h00[n]*f2
    elif iy < 2005:     # interpolate between 2000 - 2005
        f2=(iy+(iday-1)/365.25-2000)/5.
        f1=1.-f2
        for n in range(105):
            g[n]=g00[n]*f1+g05[n]*f2
            h[n]=h00[n]*f1+h05[n]*f2
    else:               # extrapolate beyond 2005:
        dt=float(iy)+float(iday-1)/365.25-2005.
        g = g05
        h = h05
        g[0:45] += dg05*dt
        h[0:45] += dh05*dt

    # coefficients for a given year have been calculated; now multiply
    # them by schmidt normalization factors:
    k = 14

    s = 1.
    mn = 1
    for n in range(1,k):
        s *= (2*n-1)/n
        g[mn] *= s      # g_n,n and h_n,n are normalized by (2n-1)/n?
        h[mn] *= s
        p = s
        for m in range(n):
            if m == 0: aa = 2
            else: aa = 1
            p *= np.sqrt(aa*(n-m)/(n+m+1))
            mn += 1
            g[mn] *= p  # g_m,n norm by sqrt(aa(n-m+1)/(n+m)), Eqn (3.2) in Winch+2005?
            h[mn] *= p
        mn += 1

    g10=-g[1]
    g11= g[2]
    h11= h[2]

    # Now calculate the components of the unit vector ezmag in geo coord.system:
    # sin(teta0)*cos(lambda0), sin(teta0)*sin(lambda0), and cos(teta0)
    #       st0 * cl0                st0 * sl0                ct0
    sq=g11**2+h11**2
    sqq=np.sqrt(sq)
    sqr=np.sqrt(g10**2+sq)
    sl0=-h11/sqq
    cl0=-g11/sqq
    st0=sqq/sqr
    ct0=g10/sqr
    stcl=st0*cl0
    stsl=st0*sl0
    ctsl=ct0*sl0
    ctcl=ct0*cl0

    gst,slong,srasn,sdec = sun(iy,iday,ihour,min,isec)
    # s1,s2, and s3 are the components of the unit vector exgsm=exgse in the
    # system gei pointing from the earth's center to the sun:
    s1=np.cos(srasn)*np.cos(sdec)
    s2=np.sin(srasn)*np.cos(sdec)
    s3=np.sin(sdec)
    cgst=np.cos(gst)
    sgst=np.sin(gst)

    # dip1, dip2, and dip3 are the components of the unit vector ezsm=ezmag in the system gei:
    dip1=stcl*cgst-stsl*sgst
    dip2=stcl*sgst+stsl*cgst
    dip3=ct0

    # Now calculate the components of the unit vector eygsm in the system gei
    # by taking the vector product d x s and normalizing it to unit length:
    y1=dip2*s3-dip3*s2
    y2=dip3*s1-dip1*s3
    y3=dip1*s2-dip2*s1
    y=np.sqrt(y1*y1+y2*y2+y3*y3)
    y1=y1/y
    y2=y2/y
    y3=y3/y

    # Then in the gei system the unit vector z = ezgsm = exgsm x eygsm = s x y has the components:
    z1=s2*y3-s3*y2
    z2=s3*y1-s1*y3
    z3=s1*y2-s2*y1

    # The vector ezgse (here dz) in gei has the components (0,-sin(delta),
    # cos(delta)) = (0.,-0.397823,0.917462); here delta = 23.44214 deg for
    # The epoch 1978 (see the book by gurevich or other astronomical handbooks).
    # Here the most accurate time-dependent formula is used:
    dj=(365*(iy-1900)+(iy-1901)/4 +iday)*-0.5+(ihour*3600+min*60+isec)/86400.
    t=dj/36525.
    obliq=(23.45229-0.0130125*t)/57.2957795
    dz1=0.
    dz2=-np.sin(obliq)
    dz3= np.cos(obliq)

    # then the unit vector eygse in gei system is the vector product dz x s :
    dy1=dz2*s3-dz3*s2
    dy2=dz3*s1-dz1*s3
    dy3=dz1*s2-dz2*s1

    # The elements of the matrix gse to gsm are the scalar products:
    # chi=em22=(eygsm,eygse), shi=em23=(eygsm,ezgse), em32=(ezgsm,eygse)=-em23,
    # and em33=(ezgsm,ezgse)=em22
    chi=y1*dy1+y2*dy2+y3*dy3
    shi=y1*dz1+y2*dz2+y3*dz3
    hi=np.arcsin(shi)

    # Tilt angle: psi=arcsin(dip,exgsm)
    sps=dip1*s1+dip2*s2+dip3*s3
    cps=np.sqrt(1.-sps**2)
    psi=np.arcsin(sps)

    # The elements of the matrix mag to sm are the scalar products:
    # cfi=gm22=(eysm,eymag), sfi=gm23=(eysm,exmag); They can be derived as follows:
    # In geo the vectors exmag and eymag have the components (ct0*cl0,ct0*sl0,-st0) and (-sl0,cl0,0), respectively.

    # Hence, in gei the components are:
    #     exmag:    ct0*cl0*cos(gst)-ct0*sl0*sin(gst)
    #               ct0*cl0*sin(gst)+ct0*sl0*cos(gst)
    #               -st0
    #     eymag:    -sl0*cos(gst)-cl0*sin(gst)
    #               -sl0*sin(gst)+cl0*cos(gst)
    #                0
    # The components of eysm in gei were found above as y1, y2, and y3;
    # Now we only have to combine the quantities into scalar products:
    exmagx=ct0*(cl0*cgst-sl0*sgst)
    exmagy=ct0*(cl0*sgst+sl0*cgst)
    exmagz=-st0
    eymagx=-(sl0*cgst+cl0*sgst)
    eymagy=-(sl0*sgst-cl0*cgst)
    cfi=y1*eymagx+y2*eymagy
    sfi=y1*exmagx+y2*exmagy+y3*exmagz

    xmut=(np.arctan2(sfi,cfi)+3.1415926536)*3.8197186342

    # The elements of the matrix geo to gsm are the scalar products:
    # a11=(exgeo,exgsm), a12=(eygeo,exgsm), a13=(ezgeo,exgsm),
    # a21=(exgeo,eygsm), a22=(eygeo,eygsm), a23=(ezgeo,eygsm),
    # a31=(exgeo,ezgsm), a32=(eygeo,ezgsm), a33=(ezgeo,ezgsm),

    # All the unit vectors in brackets are already defined in gei:
    # exgeo=(cgst,sgst,0), eygeo=(-sgst,cgst,0), ezgeo=(0,0,1)
    # exgsm=(s1,s2,s3),  eygsm=(y1,y2,y3),   ezgsm=(z1,z2,z3)
    # and therefore:
    a11=s1*cgst+s2*sgst
    a12=-s1*sgst+s2*cgst
    a13=s3
    a21=y1*cgst+y2*sgst
    a22=-y1*sgst+y2*cgst
    a23=y3
    a31=z1*cgst+z2*sgst
    a32=-z1*sgst+z2*cgst
    a33=z3

def sun(iy,iday,ihour,min,isec):
    """
    Calculates four quantities necessary for coordinate transformations
    which depend on sun position (and, hence, on universal time and season)

    :param iy: year number (four digits)
    :param iday: day of year (day 1 = Jan 1)
    :param ihour: hour of day (00 to 23)
    :param min: minute of hour (00 to 59)
    :param isec: seconds of minute (00 to 59)
    :return: gst,slong,srasn, sdec. gst - greenwich mean sidereal time, slong - longitude along ecliptic
        srasn - right ascension,  sdec - declination of the sun (radians)
        Original version of this subroutine has been compiled from: Russell, C.T., Cosmic electrodynamics, 1971, v.2, pp.184-196.


    Last modification:  March 31, 2003 (only some notation changes)
    Original version written by:    Gilbert D. Mead
    Python version by Sheng Tian
    """
    rad = 57.295779513

    if (iy < 1901) | (iy > 2099):
        raise ValueError
    fday=(ihour*3600+min*60+isec)/86400.
    dj=365*(iy-1900)+(iy-1901)/4+iday-0.5+fday
    t=dj/36525.
    vl=np.mod(279.696678+0.9856473354*dj,360.)
    gst=np.mod(279.690983+.9856473354*dj+360.*fday+180.,360.)/rad
    g=np.mod(358.475845+0.985600267*dj,360.)/rad
    slong=(vl+(1.91946-0.004789*t)*np.sin(g)+0.020094*np.sin(2.*g))/rad
    if slong > 6.2831853: slong=slong-6.2831853
    if slong< 0: slong=slong+6.2831853
    obliq=(23.45229-0.0130125*t)/rad
    sob=np.sin(obliq)
    slp=slong-9.924e-5

    # The last constant is a correction for the angular aberration due to the orbital motion of the earth
    sind=sob*np.sin(slp)
    cosd=np.sqrt(1.-sind**2)
    sc=sind/cosd
    sdec=np.arctan(sc)
    srasn=3.141592654-np.arctan2(np.cos(obliq)/sob*sc,-np.cos(slp)/cosd)

    return gst,slong,srasn,sdec



def geomag (p1,p2,p3, j):
    """
    Converts geographic (geo) to dipole (mag) coordinates or vica versa.
                   j>0                       j<0
    input:  j,xgeo,ygeo,zgeo           j,xmag,ymag,zmag
    output:    xmag,ymag,zmag           xgeo,ygeo,zgeo

    :param p1,p2,p3: input position
    :param j: flag
    :return: output position
    """

    #  Attention: subroutine  recalc  must be invoked before geomag in two cases:
    #     /a/  before the first transformation of coordinates
    #     /b/  if the values of iyear and/or iday have been changed

    # common /geopack1/ st0,ct0,sl0,cl0,ctcl,stcl,ctsl,stsl,ab(19),bb(8)
    global st0,ct0, sl0,sl0, ctcl,stcl, ctsl,stsl

    if j > 0:
        xgeo,ygeo,zgeo = [p1,p2,p3]
        xmag = xgeo*ctcl+ygeo*ctsl-zgeo*st0
        ymag = ygeo*cl0-xgeo*sl0
        zmag = xgeo*stcl+ygeo*stsl+zgeo*ct0
        return xmag,ymag,zmag
    else:
        xmag,ymag,zmag = [p1,p2,p3]
        xgeo = xmag*ctcl-ymag*sl0+zmag*stcl
        ygeo = xmag*ctsl+ymag*cl0+zmag*stsl
        zgeo = zmag*ct0-xmag*st0
        return xgeo,ygeo,zgeo

def geigeo (p1,p2,p3,j):
    """
    Converts equatorial inertial (gei) to geographical (geo) coords or vica versa.
                   j>0                       j<0
    input:  j,xgei,ygei,zgei           j,xgeo,ygeo,zgeo
    output:    xgeo,ygeo,zgeo           xgei,ygei,zgei

    :param p1,p2,p3: input position
    :param j: flag
    :return: output position
    """

    #  Attention: subroutine  recalc  must be invoked before geomag in two cases:
    #     /a/  before the first transformation of coordinates
    #     /b/  if the values of iyear and/or iday have been changed

    # common /geopack1/ a(27),cgst,sgst,b(6)
    global cgst,sgst

    if j > 0:
        xgei,ygei,zgei = [p1,p2,p3]
        xgeo = xgei*cgst+ygei*sgst
        ygeo = ygei*cgst-xgei*sgst
        zgeo = zgei
        return xgeo,ygeo,zgeo
    else:
        xgeo,ygeo,zgeo = [p1,p2,p3]
        xgei = xgeo*cgst-ygeo*sgst
        ygei = ygeo*cgst+xgeo*sgst
        zgei = zgeo
        return xgei,ygei,zgei

def magsm (p1,p2,p3,j):
    """
    Converts dipole (mag) to solar magnetic (sm) coordinates or vica versa
                   j>0                       j<0
    input:  j,xmag,ymag,zmag           j,xsm, ysm, zsm
    output:    xsm, ysm, zsm           xmag,ymag,zmag

    :param p1,p2,p3: input position
    :param j: flag
    :return: output position
    """

    #  Attention: subroutine  recalc  must be invoked before geomag in two cases:
    #     /a/  before the first transformation of coordinates
    #     /b/  if the values of iyear and/or iday have been changed

    # common /geopack1/ a(8),sfi,cfi,b(7),ab(10),ba(8)
    global sfi,cfi

    if j > 0:
        xmag,ymag,zmag = [p1,p2,p3]
        xsm = xmag*cfi-ymag*sfi
        ysm = xmag*sfi+ymag*cfi
        zsm = zmag
        return xsm,ysm,zsm
    else:
        xsm,ysm,zsm = [p1,p2,p3]
        xmag = xsm*cfi+ysm*sfi
        ymag = ysm*cfi-xsm*sfi
        zmag = zsm
        return xmag,ymag,zmag

def gsmgse (p1,p2,p3,j):
    """
    converts geocentric solar magnetospheric (gsm) coords to solar ecliptic (gse) ones or vica versa.
                   j>0                       j<0
    input:  j,xgsm,ygsm,zgsm           j,xgse,ygse,zgse
    output:    xgse,ygse,zgse           xgsm,ygsm,zgsm

    :param p1,p2,p3: input position
    :param j: flag
    :return: output position
    """

    # common /geopack1/ a(12),shi,chi,ab(13),ba(8)
    global shi,chi

    if j > 0:
        xgsm,ygsm,zgsm = [p1,p2,p3]
        xgse = xgsm
        ygse = ygsm*chi-zgsm*shi
        zgse = ygsm*shi+zgsm*chi
        return xgse,ygse,zgse
    else:
        xgse,ygse,zgse = [p1,p2,p3]
        xgsm = xgse
        ygsm = ygse*chi+zgse*shi
        zgsm = zgse*chi-ygse*shi
        return xgsm,ygsm,zgsm

def smgsm (p1,p2,p3,j):
    """
    Converts solar magnetic (sm) to geocentric solar magnetospheric (gsm) coordinates or vica versa.
                   j>0                       j<0
    input:  j,xsm, ysm, zsm           j,xgsm,ygsm,zgsm
    output:    xgsm,ygsm,zgsm           xsm, ysm, zsm

    :param p1,p2,p3: input position
    :param j: flag
    :return: output position
    """

    #  Attention: subroutine  recalc  must be invoked before geomag in two cases:
    #     /a/  before the first transformation of coordinates
    #     /b/  if the values of iyear and/or iday have been changed

    # common /geopack1/ a(10),sps,cps,b(15),ab(8)
    global sps,cps

    if j > 0:
        xsm,ysm,zsm = [p1,p2,p3]
        xgsm = xsm*cps+zsm*sps
        ygsm = ysm
        zgsm = zsm*cps-xsm*sps
        return xgsm,ygsm,zgsm
    else:
        xgsm,ygsm,zgsm = [p1,p2,p3]
        xsm = xgsm*cps-zgsm*sps
        ysm = ygsm
        zsm = xgsm*sps+zgsm*cps
        return xsm,ysm,zsm

def geogsm(p1,p2,p3,j):
    """
    Converts geographic (geo) to geocentric solar magnetospheric (gsm) coordinates or vica versa.
                   j>0                       j<0
    input:  j,xgeo,ygeo,zgeo           j,xgsm,ygsm,zgsm
    output:    xgsm,ygsm,zgsm           xgeo,ygeo,zgeo

    :param p1,p2,p3: input position
    :param j: flag
    :return: output position
    """

    #  Attention: subroutine  recalc  must be invoked before geomag in two cases:
    #     /a/  before the first transformation of coordinates
    #     /b/  if the values of iyear and/or iday have been changed

    # common /geopack1/aa(17),a11,a21,a31,a12,a22,a32,a13,a23,a33,d,b(8)
    global a11,a21,a31,a12,a22,a32,a13,a23,a33

    if j > 0:
        xgeo,ygeo,zgeo = [p1,p2,p3]
        xgsm = a11*xgeo+a12*ygeo+a13*zgeo
        ygsm = a21*xgeo+a22*ygeo+a23*zgeo
        zgsm = a31*xgeo+a32*ygeo+a33*zgeo
        return xgsm,ygsm,zgsm
    else:
        xgsm,ygsm,zgsm = [p1,p2,p3]
        xgeo = a11*xgsm+a21*ygsm+a31*zgsm
        ygeo = a12*xgsm+a22*ygsm+a32*zgsm
        zgeo = a13*xgsm+a23*ygsm+a33*zgsm
        return xgeo,ygeo,zgeo



def sphcar(p1,p2,p3, j):
    """
    Converts spherical coords into cartesian ones and vica versa (theta and phi in radians).
                  j>0            j<0
    input:   j,r,theta,phi     j,x,y,z
    output:      x,y,z        r,theta,phi

    :param r,theta,phi:
    :param x,y,z:
    :param j:
    :return:

    Note: at the poles (x=0 and y=0) we assume phi=0 (when converting from cartesian to spherical coords, i.e., for j<0)
    Last mofification: April 1, 2003 (only some notation changes and more comments added)
    Author:  N.A. Tsyganenko
    """

    if j > 0:
        r,theta,phi = [p1,p2,p3]
        sq=r*np.sin(theta)
        x=sq*np.cos(phi)
        y=sq*np.sin(phi)
        z= r*np.cos(theta)
        return x,y,z
    else:
        x,y,z = [p1,p2,p3]
        sq=x**2+y**2
        r=np.sqrt(sq+z**2)
        if sq != 0:
            sq=np.sqrt(sq)
            phi=np.arctan2(y,x)
            theta=np.arctan2(sq,z)
            if phi < 0: phi += 2*np.pi
        else:
            phi=0.
            if z < 0: theta = np.pi
            else: theta = 0
        return r,theta,phi

def bspcar (theta,phi,br,btheta,bphi):
    """
    Calculates cartesian field components from spherical ones.

    :param theta,phi: spherical angles of the point in radians
    :param br,btheta,bphi: spherical components of the field
    :return: bx,by,bz. cartesian components of the field

    # Last mofification:  April 1, 2003 (only some notation changes and more comments added)
    # Author:  N.A. Tsyganenko
    """

    s= np.sin(theta)
    c= np.cos(theta)
    sf=np.sin(phi)
    cf=np.cos(phi)
    be=br*s+btheta*c

    bx=be*cf-bphi*sf
    by=be*sf+bphi*cf
    bz=br*c-btheta*s

    return bx,by,bz

def bcarsp (x,y,z,bx,by,bz):
    """
    Calculates spherical field components from those in cartesian system

    :param x,y,z: cartesian components of the position vector
    :param bx,by,bz: cartesian components of the field vector
    :return: br,btheta,bphi. spherical components of the field vector

    Last mofification:  April 1, 2003 (only some notation changes and more comments added)
    Author:  N.A. Tsyganenko
    """

    rho2=x**2+y**2
    r=np.sqrt(rho2+z**2)
    rho=np.sqrt(rho2)

    if rho != 0:
        cphi=x/rho
        sphi=y/rho
    else:
        cphi=1.
        sphi=0.

    ct=z/r
    st=rho/r

    br=(x*bx+y*by+z*bz)/r
    btheta=(bx*cphi+by*sphi)*ct-bz*st
    bphi=by*cphi-bx*sphi

    return br,btheta,bphi


def call_external_model(exname, iopt, parmod, ps, x,y,z):
    if exname == 't89':
        return t89.t89c(iopt, parmod, ps, x,y,z)
    elif exname == 't04':
        pass
    else:
        pass

def call_internal_model(inname, x,y,z):
    if inname == 'dipole':
        return dip(x,y,z)
    elif inname == 'igrf':
        return igrf_gsm(x,y,z)
    else:
        raise ValueError

def rhand (x,y,z,iopt,parmod,exname,inname):
    """
    Calculates the components of the right hand side vector in the geomagnetic field
    line equation  (a subsidiary subroutine for the subroutine step)

    :param x,y,z:
    :param iopt:
    :param parmod:
    :param exname: name of the subroutine for the external field.
    :param inname: name of the subroutine for the internal field.

    Last mofification:  March 31, 2003
    Author:  N.A. Tsyganenko
    :return: r1,r2,r3.
    """
    #  common /geopack1/ a(15),psi,aa(10),ds3,bb(8)
    global a, psi, aa, ds3, bb

    bxgsm,bygsm,bzgsm = call_external_model(exname, iopt, parmod, psi, x,y,z)
    hxgsm,hygsm,hzgsm = call_internal_model(inname, x,y,z)

    bx=bxgsm+hxgsm
    by=bygsm+hygsm
    bz=bzgsm+hzgsm
    b=ds3/np.sqrt(bx**2+by**2+bz**2)

    r1=bx*b
    r2=by*b
    r3=bz*b

    return r1,r2,r3

def step(x,y,z, ds,errin,iopt,parmod,exname,inname):
    """
    Re-calculates {x,y,z}, making a step along a field line.
    model version, the array parmod contains input parameters for that model

    :param x,y,z: the input position
    :param ds: the step size
    :param errin: the permissible error value
    :param iopt: specifies the external model version
    :param parmod: contains input parameters for that model
    :param exname: name of the subroutine for the external field.
    :param inname: name of the subroutine for the internal field.
    :return: x,y,z. The output position

    Last mofification:  March 31, 2003
    Author:  N.A. Tsyganenko
    """

    # common /geopack1/ a(26),ds3,b(8)
    global a, ds3, b

    if errin <=0: raise ValueError
    errcur = errin
    i = 0
    maxloop = 100

    while (errcur >= errin) & (i < maxloop):
        ds3=-ds/3.
        r11,r12,r13 = rhand(x,y,z,iopt,parmod,exname,inname)
        r21,r22,r23 = rhand(x+r11,y+r12,z+r13,iopt,parmod,exname,inname)
        r31,r32,r33 = rhand(x+.5*(r11+r21),y+.5*(r12+r22),z+.5*(r13+r23),iopt,parmod,exname,inname)
        r41,r42,r43 = rhand(x+.375*(r11+3.*r31),y+.375*(r12+3.*r32),z+.375*(r13+3.*r33),iopt,parmod,exname,inname)
        r51,r52,r53 = rhand(x+1.5*(r11-3.*r31+4.*r41),y+1.5*(r12-3.*r32+4.*r42),z+1.5*(r13-3.*r33+4.*r43),iopt,parmod,exname,inname)
        errcur=np.abs(r11-4.5*r31+4.*r41-.5*r51)+np.abs(r12-4.5*r32+4.*r42-.5*r52)+np.abs(r13-4.5*r33+4.*r43-.5*r53)
        if errcur < errin: break

        ds *= 0.5
        i += 1
    else:
        print('reached maximum loop ...')
        return

    x += 0.5*(r11+4.*r41+r51)
    y += 0.5*(r12+4.*r42+r52)
    z += 0.5*(r13+4.*r43+r53)
    if (errcur < (errin*0.04)) & (np.abs(ds) < 1.33):
        ds *= 1.5

    return x,y,z

def trace(xi,yi,zi,dir,rlim,r0,iopt,parmod,exname,inname):
    """
    Traces a field line from an arbitrary point of space to the earth's surface or
    to a model limiting boundary.

    The highest order of spherical harmonics in the main field expansion used
    in the mapping is calculated automatically. if inname=igrf_gsm, then an IGRF model
    field will be used, and if inname=dip, a pure dipole field will be used.

    In any case, before calling trace, one should invoke recalc, to calculate correct
    values of the IGRF coefficients and all quantities needed for transformations
    between coordinate systems involved in this calculations.

    Alternatively, the subroutine recalc can be invoked with the desired values of
    iyear and iday (to specify the dipole moment), while the values of the dipole
    tilt angle psi (in radians) and its sine (sps) and cosine (cps) can be explicitly
    specified and forwarded to the common block geopack1 (11th, 12th, and 16th elements, resp.)

    :param xi,yi,zi: gsm coords of initial point (in earth radii, 1 re = 6371.2 km)
    :param dir: sign of the tracing direction: if
        dir=1.0 then we move antiparallel to the field vector (e.g. from northern to southern conjugate point), and if
        dir=-1.0 then the tracing goes in the opposite direction.
    :param rlim: upper limit of the geocentric distance, where the tracing is terminated.
    :param r0: radius of a sphere (in re) for which the field line endpoint coordinates xf,yf,zf should be calculated.
    :param iopt: a model index; can be used for specifying an option of the external field model (e.g., interval of the kp-index).
        Alternatively, one can use the array parmod for that purpose (see below); in that case iopt is just a dummy parameter.
    :param parmod: a 10-element array containing model parameters, needed for a unique specification of the external field.
        The concrete meaning of the components of parmod depends on a specific version of the external field model.
    :param exname: name of the subroutine for the external field.
    :param inname: name of the subroutine for the internal field.
    :return:
        xf,yf,zf. GSM coords of the last calculated point of a field line
        xx,yy,zz. Arrays containing coords of field line points. Here their maximal length was assumed equal to 999.
        l. Actual number of the calculated field line points. if l exceeds 999, tracing terminates, and a warning is displayed.

    Last mofification:  March 31, 2003
    Author:  N.A. Tsyganenko
    """

    # common /geopack1/ aa(26),dd,bb(8)
    global aa, dd, bb, ds3

    err, l, ds, x,y,z, dd, al = 0.001, 0, 0.5*dir, xi,yi,zi, dir, 0.
    xx = np.array([x])
    yy = np.array([y])
    zz = np.array([z])
    maxloop = 1000

    # Here we call RHAND just to find out the sign of the radial component of the field
    # vector, and to determine the initial direction of the tracing (i.e., either away
    # or towards Earth):
    ds3=-ds/3.
    r1,r2,r3 =  rhand(x,y,z,iopt,parmod,exname,inname)

    # |ad|=0.01 and its sign follows the rule:
    # (1) if dir=1 (tracing antiparallel to B vector) then the sign of ad is the same as of Br
    # (2) if dir=-1 (tracing parallel to B vector) then the sign of ad is opposite to that of Br
    #     ad is defined in order to initialize the value of rr (radial distance at previous step):
    ad=0.01
    if (x*r1+y*r2+z*r3) < 0: ad=-0.01

    rr=np.sqrt(x**2+y**2+z**2)+ad

    while l < maxloop:
        ryz=y**2+z**2
        r2=x**2+ryz
        r=np.sqrt(r2)

        # check if the line hit the outer tracing boundary; if yes, then terminate the tracing
        if (r > rlim) | (ryz > 1600) | (x>20): break

        # check whether or not the inner tracing boundary was crossed from outside,
        # if yes, then calculate the footpoint position by interpolation
        if (r < r0) & (rr > r):
            # find the footpoint position by interpolating between the current and previous field line points:
            r1=(r0-r)/(rr-r)
            x=x-(x-xr)*r1
            y=y-(y-yr)*r1
            z=z-(z-zr)*r1
            break

        # check if (i) we are moving outward, or (ii) we are still sufficiently
        # far from Earth (beyond R=5Re); if yes, proceed further:
        if (r >= rr) | (r > 5):
            pass
        # now we moved closer inward (between R=3 and R=5); go to 3 and begin logging
        # previous values of X,Y,Z, to be used in the interpolation (after having
        # crossed the inner tracing boundary):
        else:
            if r >= 3:
                # We entered inside the sphere R=3: to avoid too large steps (and hence inaccurate
                # interpolated position of the footpoint), enforce the progressively smaller
                # stepsize values as we approach the inner boundary R=R0:
                ds = dir
            else:
                fc = 0.2
                if (r-r0) < 0.05: fc = 0.05
                al = fc*(r-r0+0.2)
                ds = dir*al
            xr,yr,zr = [x,y,z]
        rr=r
        x,y,z = step(x,y,z,ds,err,iopt,parmod,exname,inname)
        np.append(xx,x)
        np.append(yy,y)
        np.append(zz,z)
        l += 1

    return x,y,z



def shuetal_mgnp(xn_pd,vel,bzimf,xgsm,ygsm,zgsm):
    """
    For any point of space with coordinates (xgsm,ygsm,zgsm) and specified conditions
    in the incoming solar wind, this subroutine:
        (1) determines if the point (xgsm,ygsm,zgsm) lies inside or outside the
            model magnetopause of Shue et al. (jgr-a, v.103, p. 17691, 1998).
        (2) calculates the gsm position of a point {xmgnp,ymgnp,zmgnp}, lying at the model
            magnetopause and asymptotically tending to the nearest boundary point with
            respect to the observation point {xgsm,ygsm,zgsm}, as it approaches the magnetopause.

    :param xn_pd: either solar wind proton number density (per c.c.) (if vel>0)
        or the solar wind ram pressure in nanopascals   (if vel<0)
    :param vel: either solar wind velocity (km/sec)
        or any negative number, which indicates that xn_pd stands
        for the solar wind pressure, rather than for the density
    :param bzimf: imf bz in nanoteslas
    :param xgsm,ygsm,zgsm: gsm position of the observation point in earth radii
    :return: xmgnp,ymgnp,zmgnp. GSM position of the boundary point.
        dist. Distance (in re) between the observation point (xgsm,ygsm,zgsm) and the model magnetopause
        id. position flag: id=+1 (-1) means that the observation point lies inside (outside) of the model magnetopause, respectively.

    Last mofification:  April 4, 2003
    Author:  N.A. Tsyganenko
    """

    # pd is the solar wind dynamic pressure (in npa)
    if vel < 0: pd = xn_pd
    else: pd = 1.94e-6*xn_pd*vel**2

    # Define the angle phi, measured duskward from the noon-midnight meridian plane;
    # if the observation point lies on the x axis, the angle phi cannot be uniquely
    # defined, and we set it at zero:
    if (ygsm != 0) | (zgsm != 0): phi = np.arctan2(ygsm,zgsm)
    else: phi = 0

    # First, find out if the observation point lies inside the Shue et al bdry
    # and set the value of the id flag:
    id = -1
    r0 = (10.22+1.29*np.tanh(0.184*(bzimf+8.14)))*pd**(-0.15151515)
    alpha = (0.58-0.007*bzimf)*(1.+0.024*np.log(pd))
    r = np.sqrt(xgsm**2+ygsm**2+zgsm**2)
    rm = r0*(2./(1.+xgsm/r))**alpha
    if r < rm: id = 1

    #  Now, find the corresponding t96 magnetopause position, to be used as
    #  a starting approximation in the search of a corresponding Shue et al.
    #  boundary point:
    xmt96,ymt96,zmt96,dist,id96 = t96_mgnp(pd,-1.,xgsm,ygsm,zgsm)

    rho2 = ymt96**2+zmt96**2
    r = np.sqrt(rho2+xmt96**2)
    st = np.sqrt(rho2)/r
    ct = xmt96/r

    #  Now, use newton's iterative method to find the nearest point at the Shue et al.'s boundary:
    nit = 0
    while nit < 1000:
        nit += 1

        t = np.arctan2(st,ct)
        rm = r0*(2./(1.+ct))**alpha

        f = r-rm
        gradf_r = 1.
        gradf_t = -alpha/r*rm*st/(1.+ct)
        gradf = np.sqrt(gradf_r**2+gradf_t**2)

        dr = -f/gradf**2
        dt =  dr/r*gradf_t

        r = r+dr
        t = t+dt
        st = np.sin(t)
        ct = np.cos(t)

        ds = np.sqrt(dr**2+(r*dt)**2)
        if ds <= 1.e-4: break
    else: print(' boundary point could not be found; iterations do not converge')


    xmgnp = r*np.cos(t)
    rho =   r*np.sin(t)
    ymgnp = rho*np.sin(phi)
    zmgnp = rho*np.cos(phi)

    dist = np.sqrt((xgsm-xmgnp)**2+(ygsm-ymgnp)**2+(zgsm-zmgnp)**2)

    return xmgnp,ymgnp,zmgnp, dist, id

def t96_mgnp (xn_pd,vel,xgsm,ygsm,zgsm):
    """
    For any point of space with given coordinates (xgsm,ygsm,zgsm), this subroutine defines
    the position of a point (xmgnp,ymgnp,zmgnp) at the T96 model magnetopause, having the
    same value of the ellipsoidal tau-coordinate, and the distance between them. This is
    not the shortest distance d_min to the boundary, but dist asymptotically tends to d_min,
    as the observation point gets closer to the magnetopause.

    The pressure-dependent magnetopause is that used in the t96_01 model
    (Tsyganenko, jgr, v.100, p.5599, 1995; esa sp-389, p.181, oct. 1996)

    :param xn_pd: either solar wind proton number density (per c.c.) (if vel>0)
        or the solar wind ram pressure in nanopascals   (if vel<0)
    :param vel: either solar wind velocity (km/sec)
        or any negative number, which indicates that xn_pd stands
        for the solar wind pressure, rather than for the density
    :param xgsm,ygsm,zgsm: gsm position of the observation point in earth radii
    :return: xmgnp,ymgnp,zmgnp. GSM position of the boundary point.
        dist. Distance (in re) between the observation point (xgsm,ygsm,zgsm) and the model magnetopause
        id. position flag: id=+1 (-1) means that the observation point lies inside (outside) of the model magnetopause, respectively.

    Last mofification:  April 3, 2003
    Author:  N.A. Tsyganenko
    """
    # Define solar wind dynamic pressure (nanopascals, assuming 4% of alpha-particles),
    # if not explicitly specified in the input:
    if vel < 0: pd = xn_pd
    else: pd = 1.94e-6*xn_pd*vel**2

    # ratio of pd to the average pressure, assumed equal to 2 npa:
    # The power index 0.14 in the scaling factor is the best-fit value
    # obtained from data and used in the t96_01 version
    # Values of the magnetopause parameters for  pd = 2 npa:
    rat = pd/2.0
    rat16 = rat**0.14

    a0, s00, x00 = [70.,1.08,5.48]

    # Values of the magnetopause parameters, scaled by the actual pressure:
    # xm is the x-coordinate of the "seam" between the ellipsoid and the cylinder
    # For details on the ellipsoidal coordinates, see the paper:
    # N.A. Tsyganenko, Solution of chapman-ferraro problem for an ellipsoidal magnetopause, planet.space sci., v.37, p.1037, 1989).
    a  = a0/rat16
    s0 = s00
    x0 = x00/rat16
    xm = x0-a


    if (ygsm != 0) | (zgsm != 0): phi = np.arctan2(ygsm,zgsm)
    else: phi = 0

    rho = np.sqrt(ygsm**2+zgsm**2)
    if xgsm < xm:
        xmgnp = xgsm
        rhomgnp = a*np.sqrt(s0**2-1)
        ymgnp = rhomgnp*np.sin(phi)
        zmgnp = rhomgnp*np.cos(phi)
        dist = np.sqrt((xgsm-xmgnp)**2+(ygsm-ymgnp)**2+(zgsm-zmgnp)**2)
        if rhomgnp >  rho: id =  1
        else: id = -1
        return xmgnp,ymgnp,zmgnp, dist, id

    xksi = (xgsm-x0)/a+1.
    xdzt = rho/a
    sq1 = np.sqrt((1.+xksi)**2+xdzt**2)
    sq2 = np.sqrt((1.-xksi)**2+xdzt**2)
    sigma = 0.5*(sq1+sq2)
    tau   = 0.5*(sq1-sq2)

    # Now calculate (x,y,z) for the closest point at the magnetopause
    xmgnp = x0-a*(1.-s0*tau)
    arg = (s0**2-1.)*(1.-tau**2)
    if arg < 0: arg = 0
    rhomgnp = a*np.sqrt(arg)
    ymgnp = rhomgnp*np.sin(phi)
    zmgnp = rhomgnp*np.cos(phi)

    # Now calculate the distance between the points {xgsm,ygsm,zgsm} and {xmgnp,ymgnp,zmgnp}:
    # (in general, this is not the shortest distance d_min, but dist asymptotically tends
    # to d_min, as we are getting closer to the magnetopause):
    dist = np.sqrt((xgsm-xmgnp)**2+(ygsm-ymgnp)**2+(zgsm-zmgnp)**2)
    if sigma > s0: id = -1  # id = -1 means that the point lies outside
    else: id = 1            # id =  1 means that the point lies inside

    return xmgnp,ymgnp,zmgnp, dist, id



# # tests.
#
# # test recalc.
# iyear = 2001
# iday = 1
# ihour = 2
# min = 3
# isec = 4
#
# print('Test recalc: ')
# recalc(iyear,iday,ihour,min,isec)
# print(st0, ct0, sl0, cl0)
# print(a11, a12, a13)
#
#
# # test igrf_geo.
# r = 1.1
# theta = 0.1
# phi = 0.2
# print('Test igrf_geo: ')
# b1,b2,b3 = igrf_geo(r, theta, phi)
# print(b1,b2,b3)
#
# # test sun
# print('Test sun: ')
# gst, slong, srasn, sdec = sun(iyear,iday,ihour,min,isec)
# print(gst, slong, srasn, sdec)
#
#
# # test sphcar
# print('Test sphcar: ')
# p1,p2,p3 = sphcar(r,theta,phi, 1)
# print(p1,p2,p3)
# r,theta,phi = sphcar(p1,p2,p3, -1)
# print(r,theta,phi)
#
#
# # test coord trans.
# print('Test cotrans: ')
# xgsm = 6.1
# ygsm = 0.3
# zgsm = 3.2
# print('GSM: ', xgsm,ygsm,zgsm)
# xgeo,ygeo,zgeo = geogsm(xgsm,ygsm,zgsm, -1)
# print('GEO: ', xgeo,ygeo,zgeo)
# xgse,ygse,zgse = gsmgse(xgsm,ygsm,zgsm, 1)
# print('GSE: ', xgse,ygse,zgse)
# xsm,ysm,zsm = smgsm(xgsm,ygsm,zgsm, -1)
# print('SM:  ', xsm,ysm,zsm)
# xmag,ymag,zmag = magsm(xsm,ysm,zsm, -1)
# print('MAG: ', xmag,ymag,zmag)
# xgei,ygei,zgei = geigeo(xgeo,ygeo,zgeo, -1)
# print('GEI: ', xgei,ygei,zgei)
# xmag,ymag,zmag = geomag(xgeo,ygeo,zgeo, 1)
# print('MAG2:', xmag,ymag,zmag)
#
# # test igrf_gsm and dip
# print('Test igrf_gsm and dip: ')
# b1,b2,b3 = igrf_gsm(xgsm, ygsm, zgsm)
# print(b1,b2,b3)
# b1,b2,b3 = dip(xgsm, ygsm, zgsm)
# print(b1,b2,b3)
#
# # test bspcar, bcarsp
# print('Test bspcar and bcarsp: ')
# b1,b2,b3 = bcarsp(xgsm,ygsm,zgsm, b1,b2,b3)
# print(b1,b2,b3)
# r,theta,phi = sphcar(xgsm,ygsm,zgsm, -1)
# b1,b2,b3 = bspcar(theta,phi, b1,b2,b3)
# print(b1,b2,b3)
#
# # test t96_mgnp, shuetal_mgnp.
# print('Test magnetopause models: ')
# pdyn = 10.
# vel = -1
# bz = -5
# x1,y1,z1, r, id = t96_mgnp(pdyn, vel, xgsm,ygsm,zgsm)
# print(x1,y1,z1, r)
# x1,y1,z1, r, id = shuetal_mgnp(pdyn, vel, bz, xgsm,ygsm,zgsm)
# print(x1,y1,z1, r)
#
# den = 10.
# vel = 500.
# x1,y1,z1, r, id = t96_mgnp(pdyn, vel, xgsm,ygsm,zgsm)
# print(x1,y1,z1, r)
# x1,y1,z1, r, id = shuetal_mgnp(pdyn, vel, bz, xgsm,ygsm,zgsm)
# print(x1,y1,z1, r)
#
#
#
# test trace, step, rhand.
# print('Test trace: ')
# iopt = 2
# ps = -0.533585131
# xgsm,ygsm,zgsm = [-5.1,0.3,-2.8]
# par = [2,-87,2,-5, 0,0, ps, xgsm,ygsm,zgsm]
# exname = 't89'
# inname = 'igrf'
# dir = -1
# rlim = 10
# r0 = 1.1
# xf,yf,zf = trace(xgsm,ygsm,zgsm, dir, rlim, r0, iopt, par, exname, inname)
# print('initial position: ')
# print(xgsm,ygsm,zgsm)
# print('footpoint position: ')
# print(xf,yf,zf)
