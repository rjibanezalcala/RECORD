dat = paramsanalS2;

figure
gscatter(dat.('b_R'), dat.('b_C'), dat.('Category'))
xlabel("b_R")
ylabel("b_C")
title("Valuation decision making profiles")

figure
gscatter(dat.('a_R'), dat.('a_C'), dat.('Category'))
xlabel("a_R")
ylabel("a_C")
title("Elasticity decision making profiles")