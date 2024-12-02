*pyet* - Estimation of Potential Evapotranspiration
===================================================

*pyet* is an open source Python package for the estimation of reference and potential evapotranspiration (PET) from time series data (`Pandas <https://pandas.pydata.org>`_) and gridded data (`Xarray <https://xarray.dev>`_). This allows users to estimate potential evapotranspiration and calibrate the models with just a few lines of python code.

.. grid::

    .. grid-item-card:: Getting started
        :link: user_guide/index
        :link-type: doc

        User guide on the basic concepts of Pastas.

    .. grid-item-card:: Examples
        :link: examples/index
        :link-type: doc

        Examples of *pyet* usage.

    .. grid-item-card:: Code Reference
        :link: api/index
        :link-type: doc

        *pyet* code reference.

.. grid::

    .. grid-item-card:: Publications
        :link: publications
        :link-type: doc

        Overview of publications that use *pyet*

    .. grid-item-card:: References
        :link: references
        :link-type: doc

        References used in the package.

Currently, 18 methods are implemented for calculating daily PET
-----------------------------

.. list-table:: PET Calculation Methods
   :widths: 15 15 5 5 5 5 5 5 10
   :header-rows: 1

   * - Method name
     - pyet function
     - T
     - RH
     - R
     - u2
     - Lat.
     - El.
     - Benchmarked?
   * - Penman
     - penman
     - ✓ [1]
     - ✓ [2]
     - ✓ [3]
     - ✓
     - ✓ [3]
     - ✓ [4]
     - ✓
   * - Penman-Monteith
     - pm
     - ✓ [1]
     - ✓ [2]
     - ✓ [3]
     - ✓
     - ✓ [3]
     - ✓ [4]
     - ✓
   * - ASCE-PM
     - pm_asce
     - ✓ [1]
     - ✓ [2]
     - ✓ [3]
     - ✓
     - ✓ [3]
     - ✓ [4]
     - ✓
   * - FAO-56
     - pm_fao56
     - ✓ [1]
     - ✓ [2]
     - ✓ [3]
     - ✓
     - ✓ [3]
     - ✓ [4]
     - ✓
   * - Priestley-Taylor
     - priestley_taylor
     - ✓
     - ✓ [5]
     - ✓ [5]
     - -
     - ✓ [5]
     - ✓ [4]
     - ✓
   * - Kimberly-Penman
     - kimberly_penman
     - ✓ [1]
     - ✓ [2]
     - ✓ [3]
     - ✓
     - ✓ [3]
     - ✓ [4]
     - -
   * - Thom-Oliver
     - thom_oliver
     - ✓ [1]
     - ✓ [2]
     - ✓ [3]
     - ✓
     - ✓ [3]
     - ✓ [4]
     - -
   * - Blaney-Criddle
     - blaney_criddle
     - ✓
     - - [6]
     - - [6]
     - - [6]
     - ✓
     - -
     - ✓
   * - Hamon
     - hamon
     - ✓
     - -
     - -
     - -
     - ✓
     - -
     - ✓
   * - Romanenko
     - romanenko
     - ✓
     - ✓
     - -
     - -
     - -
     - -
     - ✓
   * - Linacre
     - linacre
     - ✓ [7]
     - -
     - -
     - -
     - -
     - ✓
     - ✓
   * - Haude
     - haude
     - ✓
     - ✓ [8]
     - -
     - -
     - -
     - -
     - ✓
   * - Turc
     - turc
     - ✓
     - ✓
     - ✓
     - -
     - -
     - -
     - ✓
   * - Jensen-Haise
     - jensen_haise
     - ✓
     - -
     - ✓ [9]
     - -
     - ✓ [9]
     - -
     - ✓
   * - McGuinness-Bordne
     - mcguinness_bordne
     - ✓
     - -
     - -
     - -
     - ✓
     - -
     - ✓
   * - Hargreaves
     - hargreaves
     - ✓ [10]
     - -
     - -
     - -
     - ✓
     - -
     - ✓
   * - FAO-24 radiation
     - fao_24
     - ✓
     - ✓
     - ✓
     - ✓
     - -
     - ✓ [4]
     - -
   * - Abtew
     - abtew
     - ✓
     - -
     - ✓
     - -
     - -
     - -
     - ✓
   * - Makkink
     - makkink
     - ✓
     - -
     - ✓
     - -
     - -
     - ✓ [4]
     - ✓
   * - Oudin
     - oudin
     - ✓
     - -
     - -
     - -
     - ✓
     - -
     - -

.. rubric:: Footnotes

.. [1] T_max and T_min can also be provided.
.. [2] RH_max and RH_min can also be provided. If actual vapor pressure is provided, RH is not needed.
.. [3] Input for radiation can be (1) Net radiation, (2) solar radiation, or (3) sunshine hours. If (1), then latitude is not needed. If (1, 3) then latitude and elevation are needed.
.. [4] One must provide either the atmospheric pressure or elevation.
.. [5] If net radiation is provided, RH and Lat are not needed.
.. [6] If method==2, u2, RH_min, and sunshine hours are required.
.. [7] Additional input of Tmax and Tmin, or Tdew.
.. [8] Input can be RH or actual vapor pressure.
.. [9] If method==1, latitude is needed instead of Rs.
.. [10] Tmax and Tmin also needed.


Using *pyet*? Show your support by citing us!
---------------------------------------------

If you find *pyet* useful and use it in your research or project, we kindly ask you to cite the *pyet* preprint published in Hydrology and Earth System Sciences (HESS) as follows:

- Vremec, M., Collenteur, R., and Birk, S.: PyEt v1.3.1: a Python package for the estimation of potential evapotranspiration, Geosci. Model Dev. Discuss. [preprint], https://doi.org/10.5194/gmd-2024-63, in review, 2024.