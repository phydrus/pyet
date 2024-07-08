"""The rad_utils module contains utility functions for radiation data.

"""

from numpy import sqrt, clip, newaxis

from pandas import Series

from xarray import DataArray

from .meteo_utils import calc_ea, extraterrestrial_r, daylight_hours

from .utils import get_index, check_rad, vectorize

# Stefan Boltzmann constant - hourly [MJm-2K-4h-1]
STEFAN_BOLTZMANN_HOUR = 2.042 * 10**-10
# Stefan Boltzmann constant - daily [MJm-2K-4d-1]
STEFAN_BOLTZMANN_DAY = 4.903 * 10**-9


def calc_rad_net(
    tmean,
    rn=None,
    rs=None,
    lat=None,
    n=None,
    nn=None,
    tmax=None,
    tmin=None,
    rhmax=None,
    rhmin=None,
    rh=None,
    elevation=None,
    rso=None,
    a=1.35,
    b=-0.35,
    ea=None,
    albedo=0.23,
    as1=0.25,
    bs1=0.5,
    kab=None,
):
    """Net radiation [MJ m-2 d-1].

    Parameters
    ----------
    tmean: pandas.Series/xarray.DataArray
        average day temperature [°C].
    rn: float or pandas.Series or xarray.DataArray, optional
        net radiation [MJ m-2 d-1].
    rs: float or pandas.Series or xarray.DataArray, optional
        incoming solar radiation [MJ m-2 d-1].
    lat: float/xarray.DataArray, optional
        the site latitude [rad].
    n: float or pandas.Series or xarray.DataArray, optional
        actual duration of sunshine [hour].
    nn: float or pandas.Series or xarray.DataArray, optional
        maximum possible duration of sunshine or daylight hours [hour].
    tmax: float or pandas.Series or xarray.DataArray, optional
        maximum day temperature [°C].
    tmin: float or pandas.Series or xarray.DataArray, optional
        minimum day temperature [°C].
    rhmax: float or pandas.Series or xarray.DataArray, optional
        maximum daily relative humidity [%].
    rhmin: float or pandas.Series or xarray.DataArray, optional
        mainimum daily relative humidity [%].
    rh: float or pandas.Series or xarray.DataArray, optional
        mean daily relative humidity [%].
    elevation: float/xarray.DataArray, optional
        the site elevation [m].
    rso: float or pandas.Series or xarray.DataArray, optional
        clear-sky solar radiation [MJ m-2 day-1].
    a: float, optional
        empirical coefficient for Net Long-Wave radiation [-].
    b: float, optional
        empirical coefficient for Net Long-Wave radiation [-].
    ea: float or pandas.Series or xarray.DataArray, optional
        actual vapor pressure [kPa].
    albedo: float, optional
        surface albedo [-]
    as1: float, optional
        regression constant,  expressing the fraction of extraterrestrial reaching the
        earth on overcast days (n = 0) [-]
    bs1: float, optional
        empirical coefficient for extraterrestrial radiation [-]
    kab: float, optional
        coefficient derived from as1, bs1 for estimating clear-sky radiation [degrees].

    Returns
    -------
    float or pandas.Series or xarray.DataArray, optional containing the calculated net
    shortwave radiation.

    Notes
    -----
    Based on equation 40 in :cite:t:`allen_crop_1998`.

    """
    if rn is not None:
        rn = check_rad(rn)
        return rn
    else:
        if rs is None:
            rs = calc_rad_sol_in(n, lat, as1=as1, bs1=bs1, nn=nn)
        rns = calc_rad_short(
            rs=rs, lat=lat, n=n, nn=nn, albedo=albedo, as1=as1, bs1=bs1
        )  # [MJ/m2/d]
        rnl = calc_rad_long(
            rs=rs,
            tmean=tmean,
            tmax=tmax,
            tmin=tmin,
            rhmax=rhmax,
            rhmin=rhmin,
            rh=rh,
            elevation=elevation,
            lat=lat,
            rso=rso,
            a=a,
            b=b,
            ea=ea,
            kab=kab,
        )  # [MJ/m2/d]
        rn = rns - rnl
        rn = check_rad(rn)
        return rn


def calc_rad_long(
    rs,
    tmean=None,
    tmax=None,
    tmin=None,
    rhmax=None,
    rhmin=None,
    rh=None,
    elevation=None,
    lat=None,
    rso=None,
    a=1.35,
    b=-0.35,
    ea=None,
    kab=None,
):
    """Net longwave radiation [MJ m-2 d-1].

    Parameters
    ----------
    rs: float or pandas.Series or xarray.DataArray, optional
        incoming solar radiation [MJ m-2 d-1].
    tmean: float or pandas.Series or xarray.DataArray, optional
        average day temperature [°C].
    tmax: float or pandas.Series or xarray.DataArray, optional
        maximum day temperature [°C].
    tmin: float or pandas.Series or xarray.DataArray, optional
        minimum day temperature [°C].
    rhmax: float or pandas.Series or xarray.DataArray, optional
        maximum daily relative humidity [%].
    rhmin: float or pandas.Series or xarray.DataArray, optional
        mainimum daily relative humidity [%].
    rh: float or pandas.Series or xarray.DataArray, optional
        mean daily relative humidity [%].
    elevation: float/xarray.DataArray, optional
        the site elevation [m].
    lat: float/xarray.DataArray, optional
        the site latitude [rad].
    rso: float or pandas.Series or xarray.DataArray, optional
        clear-sky solar radiation [MJ m-2 day-1].
    a: float, optional
        empirical coefficient for Net Long-Wave radiation [-].
    b: float, optional
        empirical coefficient for Net Long-Wave radiation [-].
    ea: float or pandas.Series or xarray.DataArray, optional
        actual vapor pressure [kPa].
    kab: float, optional
        coefficient that can be derived from the as and bs coefficients of the
        Angstrom formula, where Kab = as + bs, and where Kab represents the
        fraction of extraterrestrial radiation reaching the earth on clear-sky
        days [-].

    Returns
    -------
    float or pandas.Series or xarray.DataArray, optional containing the calculated net
    longwave radiation.

    Notes
    -----
    Based on equation 39 in :cite:t:`allen_crop_1998`.

    """
    if ea is None:
        ea = calc_ea(tmean=tmean, tmax=tmax, tmin=tmin, rhmax=rhmax, rhmin=rhmin, rh=rh)

    if rso is None:
        tindex = get_index(rs)
        ra = extraterrestrial_r(tindex, lat)
        rso = calc_rso(ra=ra, elevation=elevation, kab=kab)
    # Add a small constant to rso where it is zero to avoid division with zero
    rso = rso.where(rso != 0, 0.001)
    if len(rs.shape) == 3 and len(rso.shape) == 1:
        rso = rso.values[:, newaxis, newaxis]
    solar_rat = clip(rs.values / rso.values, 0.3, 1)
    if tmax is not None:
        tmp1 = STEFAN_BOLTZMANN_DAY * ((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2
    else:
        tmp1 = STEFAN_BOLTZMANN_DAY * (tmean + 273.16) ** 4
    tmp2 = 0.34 - 0.14 * sqrt(ea)  # OK
    tmp3 = a * solar_rat + b  # OK
    tmp3 = clip(tmp3, 0.05, 1)
    rnl = tmp1 * tmp2 * tmp3
    return rnl


def calc_rad_short(rs=None, lat=None, albedo=0.23, n=None, nn=None, as1=0.25, bs1=0.5):
    """Net shortwave radiation [MJ m-2 d-1].

    Parameters
    ----------
    rs: float or pandas.Series or xarray.DataArray, optional
        incoming solar radiation [MJ m-2 d-1].
    lat: float, optional
        the site latitude [rad].
    albedo: float or pandas.Series or xarray.DataArray, optional
        surface albedo [-].
    n: pandas.Series/xarray.DataArray, optional
        actual duration of sunshine [hour].
    as1: float, optional
        regression constant,  expressing the fraction of extraterrestrial reaching the
        earth on overcast days (n = 0) [-].
    bs1: float, optional
        empirical coefficient for extraterrestrial radiation [-].
    nn: float or pandas.Series or xarray.DataArray, optional
        maximum possible duration of sunshine or daylight hours [hour].

    Returns
    -------
    float or pandas.Series or xarray.DataArray, optional containing the calculated
    net shortwave radiation.

    Notes
    -----
    Based on equation 38 in :cite:t:`allen_crop_1998`.

    """
    (vrs,) = vectorize(rs)
    if vrs is not None:
        return (1 - albedo) * vrs
    else:
        return (1 - albedo) * calc_rad_sol_in(n, lat, as1=as1, bs1=bs1, nn=nn)


def calc_rad_sol_in(n, lat, as1=0.25, bs1=0.5, nn=None):
    """Incoming solar radiation [MJ m-2 d-1].

    Parameters
    ----------
    n: pandas.Series or xarray.DataArray
        actual duration of sunshine [hour].
    lat: float, optional
        the site latitude [rad].
    as1: float, optional
        regression constant,  expressing the fraction of extraterrestrial reaching the
        earth on overcast days (n = 0) [-].
    bs1: float, optional
        empirical coefficient for extraterrestrial radiation [-].
    nn: pandas.Series/float, optional
        maximum possible duration of sunshine or daylight hours [hour].

    Returns
    -------
    pandas.Series containing the calculated net shortwave radiation.

    Notes
    -----
    Based on equation 35 in :cite:t:`allen_crop_1998`.

    """
    tindex = get_index(n)
    ra = extraterrestrial_r(tindex, lat)
    if nn is None:
        nn = daylight_hours(tindex, lat)
    return (as1 + bs1 * n.values / nn) * ra


def calc_rso(ra, elevation, kab=None):
    """Clear-sky solar radiation [MJ m-2 day-1].

    Parameters
    ----------
    ra: pandas.Series/xarray.DataArray, optional
        Extraterrestrial daily radiation [MJ m-2 d-1].
    elevation: float/xarray.DataArray, optional
        the site elevation [m].
    kab: float, optional
        coefficient that can be derived from the as and bs coefficients of the
        Angstrom formula, where Kab = as + bs, and where Kab represents the
        fraction of extraterrestrial radiation reaching the earth on clear-sky
        days [-].

    Returns
    -------
    pandas.Series/xarray.DataArray, optional containing the calculated Clear-sky solar
    radiation.

    Notes
    -----
    Based on equation 37 in :cite:t:`allen_crop_1998`.

    """
    if isinstance(elevation, DataArray):
        tindex = get_index(ra)
        elevation = elevation.expand_dims(dim={"time": tindex}, axis=0)
        if isinstance(ra, Series):
            ra = ra.values[:, newaxis, newaxis]
    if kab is None:
        return (0.75 + (2 * 10**-5) * elevation) * ra
    else:
        return kab * ra
