"""The radiation module contains functions of radiation PET methods

"""

from numpy import sqrt, log
from xarray import DataArray
from pandas import Series ,to_datetime
from .meteo_utils import extraterrestrial_r, calc_press, calc_psy, calc_vpc, calc_lambda
from .utils import get_index, check_rad, clip_zeros, pet_out, check_rh


def turc(tmean, rs, rh, k=0.013, clip_zero=True):
    """Potential evapotranspiration calculated according to
    :cite:t:`turc_estimation_1961`.

    Parameters
    ----------
    tmean: pandas.Series or xarray.DataArray
        average day temperature [°C].
    rs: pandas.Series or xarray.DataArray
        incoming solar radiation [MJ m-2 d-1].
    rh: pandas.Series or xarray.DataArray
        mean daily relative humidity [%].
    k: float, optional
        calibration coefficient [-].
    clip_zero: bool, optional
        if True, replace all negative values with 0.

    Returns
    -------
    pandas.Series or xarray.DataArray containing the calculated
            Potential evapotranspiration [mm d-1].

    Examples
    --------
    >>> pet_turc = turc(tmean, rs, rh)

    Notes
    -----
    Based on equation S9.10 and S9.11 in :cite:t:`mcmahon_estimating_2013`.

    .. math:: PET=k(\\frac{T_{mean}}{T_{mean}+15})(23.88R_s+50)0.013;
        for RH>50

    .. math:: PET=k(1+\\frac{50-RH}{70})(\\frac{T_{mean}}{T_{mean}+15})
        (23.88R_s+50)0.013; for RH<50

    """
    c = tmean / tmean
    c = c.where(check_rh(rh) >= 50, 1 + (50 - rh) / 70)
    pet = k * c * tmean / (tmean + 15) * (check_rad(rs) * 23.88 + 50)
    pet = clip_zeros(pet, clip_zero)
    return pet_out(tmean, pet, "Turc")


def jensen_haise(tmean, rs=None, cr=0.025, tx=-3, lat=None, method=0, clip_zero=True):
    """Potential evapotranspiration calculated accordinf to
    :cite:t:`jensen_estimating_1963`.

    Parameters
    ----------
    tmean: pandas.Series orxarray.DataArray
        average day temperature [°C].
    rs: pandas.Series or xarray.DataArray, optional
        incoming solar radiation [MJ m-2 d-1].
    cr: float, optional
        temperature coefficient [-].
    tx: float, optional
        intercept of the temperature axis [°C].
    lat: float/xarray.DataArray
        the site latitude [rad].
    method: float, optional
        0 => after :cite:t:`jensen_evaporation_2016`
        1 => after :cite:t:`oudin_which_2005`.
    clip_zero: bool, optional
        if True, replace all negative values with 0.

    Returns
    -------
    pandas.Series or xarray.DataArray containing the calculated potential
    evapotranspiration [mm d-1].

    Examples
    --------
    >>> pet_jh = jensen_haise(tmean, lat)

    Notes
    -----
    Method = 0: Based on :cite:t:`jensen_evaporation_2016`.

    .. math:: PET = \\frac{C_r(T_{mean}-T_x)R_s}{\\lambda}

    Method = 1: Based on :cite:t:`oudin_which_2005`.

    .. math:: PET = \\frac{R_a(T_{mean}+5)}{68\\lambda}

    """
    lambd = calc_lambda(tmean)
    if method == 0:
        if rs is None:
            raise Exception("If you choose method == 0, provide rs!")
        pet = check_rad(rs) / lambd * cr * (tmean - tx)
    elif method == 1:
        if lat is None:
            raise Exception("If you choose method == 1, provide lat!")
        index = get_index(tmean)
        ra = extraterrestrial_r(index, lat)
        
        temp = (tmean + 5) / 68 / lambd
        temp.index = to_datetime(temp.index)
        pet = ra * temp
    else:
        raise Exception("Method can be either 0 or 1.")
    pet = clip_zeros(pet, clip_zero)
    return pet_out(tmean, pet, "Jensen_Haise")


def mcguinness_bordne(tmean, lat, k=0.0147, clip_zero=True):
    """Potential evapotranspiration calculated according to
    :cite:t:`mcguinness_comparison_1972`.

    Parameters
    ----------
    tmean: pandas.Series or xarray.DataArray
        average day temperature [°C].
    lat: float/xarray.DataArray, optional
        the site latitude [rad].
    k: float, optional
        calibration coefficient [-].
    clip_zero: bool, optional
        if True, replace all negative values with 0.

    Returns
    -------
    pandas.Series or xarray.DataArray containing the calculated potential
    evapotranspiration [mm d-1].

    Examples
    --------
    >>> pet_mcguinness_bordne = mcguinness_bordne(tmean, lat)

    Notes
    -----
    Based on equation 13 in :cite:t:`xu_evaluation_2000`.

    .. math:: PET = k\\frac{R_a (T_{mean} + 5)}{\\lambda}

    """
    lambd = calc_lambda(tmean)
    index = get_index(tmean)
    ra = extraterrestrial_r(index, lat)
    if isinstance(tmean, DataArray) and isinstance(ra, Series):
        ra = ra.values[:, None, None]
    temp = (tmean + 5) / lambd
    temp.index = to_datetime(temp.index)
    pet = k * ra * temp
    pet = clip_zeros(pet, clip_zero)
    return pet_out(tmean, pet, "Mcguinness_Bordne")


def hargreaves(tmean, tmax, tmin, lat, k=0.0135, method=0, clip_zero=True):
    """Potential evapotranspiration calculated according to
    :cite:t:`hargreaves_estimating_1982`.

    Parameters
    ----------
    tmean: pandas.Series or xarray.DataArray
        average day temperature [°C].
    tmax: pandas.Series or xarray.DataArray
        maximum day temperature [°C].
    tmin: pandas.Series or xarray.DataArray
        minimum day temperature [°C].
    lat: float/xarray.DataArray
        the site latitude [rad].
    k: float, optional
        calirbation coefficient [-].
    method: float, optional
        0 => after :cite:t:`jensen_evaporation_2016`
        1 => after :cite:t:`mcmahon_estimating_2013`.
    clip_zero: bool, optional
        if True, replace all negative values with 0.

    Returns
    -------
    pandas.Series or xarray.DataArray containing the calculated potential
    evapotranspiration [mm d-1].

    Examples
    --------
    >>> pet_har = hargreaves(tmean, tmax, tmin, lat)

    Notes
    -----
    Method = 0; Based on equation (8-16) in :cite:t:`jensen_evaporation_2016`.

    .. math:: PET = k \\frac{R_a (T_{mean}+17.8)\\sqrt{(T_{max}-T_{min})}}\
        {\\lambda}

    Method = 1; Based on :cite:t:`mcmahon_estimating_2013`.

    .. math:: PET = chs k \\frac{R_a (T_{mean}+17.8)\\sqrt{(T_{max}-T_{min})}}\
        {\\lambda}

    , where

    .. math:: chs=0.00185*(T_{max}-T_{min})^2-0.0433*(T_{max}-T_{min})+0.4023

    """
    lambd = calc_lambda(tmean)
    index = get_index(tmean)
    ra = extraterrestrial_r(index, lat)
    if isinstance(tmean, DataArray) and isinstance(ra, Series):
        ra = ra.values[:, None, None]
    else:
        ra = ra.values
    chs = 0.00185 * (tmax - tmin) ** 2 - 0.0433 * (tmax - tmin) + 0.4023
    if method == 0:
        pet = k / 0.0135 * 0.0023 * (tmean + 17.8) * sqrt(tmax - tmin) * ra / lambd
    elif method == 1:
        pet = k * chs * sqrt(tmax - tmin) * ra / lambd * (tmean + 17.8)
    else:
        raise Exception("Method can be either 0 or 1.")
    pet = clip_zeros(pet, clip_zero)
    return pet_out(tmean, pet, "Hargreaves")


def fao_24(
    tmean, wind, rs, rh, pressure=None, elevation=None, albedo=0.23, clip_zero=True
):
    """Potential evapotranspiration calculated according to
    :cite:t:`jensen_evapotranspiration_1990`.

    Parameters
    ----------
    tmean: pandas.Series or xarray.DataArray
        average day temperature [°C].
    wind: pandas.Series xarray.DataArray
        mean day wind speed [m/s].
    rs: pandas.Series xarray.DataArray
        incoming solar radiation [MJ m-2 d-1].
    rh: pandas.Series or xarray.DataArray
        mean daily relative humidity [%].
    pressure: pandas.Series or xarray.DataArray, optional
        atmospheric pressure [kPa].
    elevation: float/xarray.DataArray, optional
        the site elevation [m].
    albedo: float/xarray.DataArray, optional
        surface albedo [-].
    clip_zero: bool, optional
        if True, replace all negative values with 0.

    Returns
    -------
    pandas.Series or xarray.DataArray containing the calculated potential
    evapotranspiration [mm d-1].

    Examples
    --------
    >>> pet_fao24 = fao_24(tmean, wind, rs, rh, elevation=elevation)

    .. math:: PE = \\frac{- 0.3 \\Delta + R_s (1-\\alpha) w}\
        {\\lambda(\\Delta +\\gamma)}
    .. math:: w = 1.066-0.13*\\frac{rh}{100}+0.045*u_2-0.02*\\frac{rh}{100}\
        *u_2-3.15*(\\frac{rh}{100})^2-0.0011*u_2

    """
    pressure = calc_press(elevation, pressure)
    gamma = calc_psy(pressure)
    dlt = calc_vpc(tmean)
    lambd = calc_lambda(tmean)

    w = (
        1.066
        - 0.13 * check_rh(rh) / 100
        + 0.045 * wind
        - 0.02 * rh / 100 * wind
        - 0.315 * (rh / 100) ** 2
        - 0.0011 * wind
    )
    pet = -0.3 + dlt / (dlt + gamma) * check_rad(rs) * (1 - albedo) * w / lambd
    pet = clip_zeros(pet, clip_zero)
    return pet_out(tmean, pet, "FAO_24")


def abtew(tmean, rs, k=0.53, clip_zero=True):
    """Potential evapotranspiration calculated according to
    :cite:t:`abtew_evapotranspiration_1996`.

    Parameters
    ----------
    tmean: pandas.Series or xarray.DataArray
        average day temperature [°C].
    rs: pandas.Series or xarray.DataArray
        incoming solar radiation [MJ m-2 d-1].
    k: float, optional
        calibration coefficient [-].
    clip_zero: bool, optional
        if True, replace all negative values with 0.

    Returns
    -------
    pandas.Series or xarray.DataArray containing the calculated potential
    evapotranspiration [mm d-1].

    Examples
    --------
    >>> pet_abtew = abtew(tmean, rs)

    Notes
    -----
    Based on equation 14 in :cite:t:`xu_evaluation_2000`.

    .. math:: PE = \\frac{k R_s}{\\lambda}

    """
    lambd = calc_lambda(tmean)
    pet = k * check_rad(rs) / lambd
    pet = clip_zeros(pet, clip_zero)
    return pet_out(tmean, pet, "Abtew")


def makkink(tmean, rs, pressure=None, elevation=None, k=0.65, clip_zero=True):
    """Potential evapotranspiration calculated according to
    :cite:t:`makkink_testing_1957`.

    Parameters
    ----------
    tmean: pandas.Series or xarray.DataArray
        average day temperature [°C].
    rs: pandas.Series or xarray.DataArray
        incoming solar radiation [MJ m-2 d-1].
    pressure: pandas.Series or xarray.DataArray, optional
        atmospheric pressure [kPa].
    elevation: float/xarray.DataArray, optional
        the site elevation [m].
    k: float, optional
        calirbation coefficient [-].
    clip_zero: bool, optional
        if True, replace all negative values with 0.

    Returns
    -------
    pandas.Series or xarray.DataArray containing the calculated potential
    evapotranspiration [mm d-1].

    Examples
    --------
    >>> pet_mak = makkink(tmean, rs, elevation=elevation)

    Notes
    -----

    .. math:: PET = \\frac{0.65 \\Delta (R_s)}{\\lambda(\\Delta +\\gamma)}

    """
    pressure = calc_press(elevation, pressure)
    gamma = calc_psy(pressure)
    dlt = calc_vpc(tmean)
    lambd = calc_lambda(tmean)
    pet = k * dlt / (dlt + gamma) * check_rad(rs) / lambd
    pet = clip_zeros(pet, clip_zero)
    return pet_out(tmean, pet, "Makkink")


def makkink_knmi(tmean, rs, clip_zero=True):
    """Potential evapotranspiration calculated according to The Royal Netherlands
    Meteorological Institute (KNMI)

    Parameters
    ----------
    tmean : pandas.Series or xarray.DataArray
        average day temperature [°C].
    rs : pandas.Series or xarray.DataArray
        incoming solar radiation [MJ m-2 d-1].
    clip_zero: bool, optional
        if True, replace all negative values with 0.

    Returns
    -------
    pandas.Series or xarray.DataArray containing the calculated potential
    evapotranspiration [mm d-1].

    Examples
    --------
    >>> pet_mak = makkink_knmi(tmean, rs)

    Notes
    ----
    This method is only applicable to the Netherlands (~sea level) due to some
    emperical values. Calculating the Makkink evaporation with the original
    formula is more suitable for general purposes. To obtain the same value as
    EV24 round the value up to one decimal.
    """
    pet = (
        650
        * (
            1
            - (0.646 + 0.0006 * tmean)
            / (
                7.5
                * log(10)
                * 6.107
                * 10 ** (7.5 * (1 - 1 / (1 + tmean / 237.3)))
                / (237.3 * (1 + tmean / 237.3) * (1 + tmean / 237.3))
                + 0.646
                + 0.0006 * tmean
            )
        )
        / (2501 - 2.38 * tmean)
        * rs
    )
    pet = clip_zeros(pet, clip_zero)
    return pet_out(tmean, pet, "Makkink_KNMI")


def oudin(tmean, lat, k1=100, k2=5, clip_zero=True):
    """Potential evapotranspiration calculated according to :cite:t:`oudin_which_2005`.

    Parameters
    ----------
    tmean: pandas.Series or xarray.DataArray
        average day temperature [°C].
    lat: float or xarray.DataArray
        the site latitude [rad].
    k1: float, optional
        calibration coefficient [-].
    k2: float, optional
        calibration coefficient [-].
    clip_zero: bool, optional
        if True, replace all negative values with 0.

    Returns
    -------
    pandas.Series or xarray.DataArray containing the calculated potential
    evapotranspiration [mm d-1].
    clip_zero: bool, optional
        if True, replace all negative values with 0.

    Examples
    --------
    >>> pet_oudin = oudin(tmean, lat)

    Notes
    -----
    Based on equation 3 in :cite:t:`oudin_which_2005`.

    .. math:: PET = \\frac{R_a (T_{mean} +5)}{\\lambda 100}; if T_{mean}+5>0
        else: PET = 0

    """
    lambd = calc_lambda(tmean)
    index = get_index(tmean)
    ra = extraterrestrial_r(index, lat)    
    temp = (tmean + k2) / lambd / k1
    temp.index = to_datetime(temp.index)
    pet = ra * temp
    # pet = pet.where((tmean + k2) >= 0, 0)
    # the above line of code is not working properly and setting all the values in pet 0.0
    pet = clip_zeros(pet, clip_zero)
    return pet_out(tmean, pet, "Oudin")
