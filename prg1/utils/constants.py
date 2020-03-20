
GE = 3.986005e14  # [m^3/s^2] Geozentrische Gravitationskonstante
OMEGA_E_DOT = 7.2921151467e-5  # [rad/s] Erdrotatiosgeschwindigkeit

REGEX_TLE_TITLE = r"^.{24}$"
REGEX_TLE_1 = r"^1\ (\ *\d{1,5})([UCS])\ (\d\d)(\d{3})([\ \w]{3})\ (\d\d)(([\ \d]{3})(\.\d{8}))\ ([\+\-\ ]\.\d{8})\ ([\+\-\ ](\d{5})([\+\-]\d))\ ([\+\-\ ](\d{5})([\+\-]\d))\ (\d)\ ([\ \d]{4})(\d)$"
REGEX_TLE_2 = r"^2\ ([\ \d]{5})\ ([\ \d]{3}\.[\d]{4})\ ([\ \d]{3}\.[\d]{4})\ ([\ \d]{7})\ ([\ \d]{3}\.[\d]{4})\ ([\ \d]{3}\.[\d]{4})\ ([\ \d]{2}.[\ \d]{8})([\ \d]{5})(\d)$"
