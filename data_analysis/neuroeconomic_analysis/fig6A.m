syms R C

xs = [.005 .02 .05 .09];
xs_cont = linspace(xs(1), xs(4), 1000);

%% Figure A
figure()
t = tiledlayout(3,2);
xs = xs';

% reward valuation
nexttile
low_valuation = [0; .1; 1; .9]; % raissa 06-22-2022
high_valuation = [2/3; 1; 1; 1]; % raissa 01-06-2022
low_sigmoid = fit(xs,low_valuation,fittype('1/(1+exp(-a*x+b))'), 'StartPoint',[1; 0]);
high_sigmoid = fit(xs,high_valuation,fittype('1/(1+exp(-a*x+b))'), 'StartPoint',[1; 0]);
fplot(1./(1+exp(-low_sigmoid.a*R+low_sigmoid.b)), 'r', 'LineWidth', 5)
hold on
fplot(1./(1+exp(-high_sigmoid.a*R+high_sigmoid.b)), 'b', 'LineWidth', 5)
scatter(xs, low_valuation, 100, 'r', 'filled')
scatter(xs, high_valuation, 100, 'b', 'filled')
title("Reward valuation")
set(gca,'XTick',[], 'FontSize',10)
xlim([xs(1) xs(4)])
ylim([0 1])
hold off

% cost valuation
nexttile
low_valuation = [.408654; .25; .204044; .110632]; % aladdin
high_valuation = [.244635; .111111; .094254; .0303571]; % simba
low_sigmoid = fit(xs,low_valuation,fittype('1/(1+exp(-a*x+b))'), 'StartPoint',[1; 0]);
high_sigmoid = fit(xs,high_valuation,fittype('1/(1+exp(-a*x+b))'), 'StartPoint',[1; 0]);
fplot(1./(1+exp(-low_sigmoid.a*C+low_sigmoid.b)), 'b', 'LineWidth', 5)
hold on
fplot(1./(1+exp(-high_sigmoid.a*C+high_sigmoid.b)), 'r', 'LineWidth', 5)
scatter(xs, low_valuation, 100, 'b', 'filled')
scatter(xs, high_valuation, 100, 'r', 'filled')
title("Cost valuation")
set(gca,'XTick',[], 'FontSize',10)
xlim([xs(1) xs(4)])
hold off

% reward elasticity
nexttile
low_elasticity = [.45; .125; 8/11; 7/11]; % raissa 04-08-2022
high_elasticity = [0; .1; 1; .9]; % raissa 06-22-2022
low_sigmoid = fit(xs,low_elasticity,fittype('1/(1+exp(-a*x+b))'), 'StartPoint',[1; 0]);
high_sigmoid = fit(xs,high_elasticity,fittype('1/(1+exp(-a*x+b))'), 'StartPoint',[1; 0]);
fplot(1./(1+exp(-low_sigmoid.a*R+low_sigmoid.b)), 'b', 'LineWidth', 5)
hold on
fplot(1./(1+exp(-high_sigmoid.a*R+high_sigmoid.b)), 'r', 'LineWidth', 5)
scatter(xs, low_elasticity, 100, 'b', 'filled')
scatter(xs, high_elasticity, 100, 'r', 'filled')
title("Reward elasticity")
set(gca,'XTick',[], 'FontSize',10)
xlim([xs(1) xs(4)])
ylim([0 1])
hold off

% Cost elasticity
nexttile
low_elasticity = [0.32377; 0.388889; .302703; .2875]; % fiona
high_elasticity = [.408654; .25; .204044; .110632]; % aladdin
low_sigmoid = fit(xs,low_elasticity,fittype('1/(1+exp(-a*x+b))'), 'StartPoint',[1; 0]);
high_sigmoid = fit(xs,high_elasticity,fittype('1/(1+exp(-a*x+b))'), 'StartPoint',[1; 0]);
fplot(1./(1+exp(-low_sigmoid.a*C+low_sigmoid.b)), 'b', 'LineWidth', 5)
hold on
fplot(1./(1+exp(-high_sigmoid.a*C+high_sigmoid.b)), 'r', 'LineWidth', 5)
scatter(xs, low_elasticity, 100, 'b', 'filled')
scatter(xs, high_elasticity, 100, 'r', 'filled')
title("Cost elasticity")
set(gca,'XTick',[], 'FontSize',10)
xlim([xs(1) xs(4)])
hold off

% Sensitivity (sensitive example)
nexttile
ys_sensitive = [0; 0.1; 1; 1]; % alexis 04-19-2022
sigmoid = fit(xs,ys_sensitive,fittype('1/(1+exp(-a*x+b))'), 'StartPoint',[1; 0]);
conf = confint(sigmoid, .8);
scatter(xs, ys_sensitive, 100, 'k', 'filled')
hold on
fplot(1./(1+exp(-sigmoid.a*R+sigmoid.b)), 'k', 'LineWidth', 5)
a_low = 1./(1+exp(-conf(1,1)*xs_cont+sigmoid.b));
a_high = 1./(1+exp(-conf(2,1)*xs_cont+sigmoid.b));
x_range = [xs_cont, fliplr(xs_cont)];
a_inBetween = [a_low, fliplr(a_high)];
fill(x_range, a_inBetween, 'k', 'EdgeAlpha', 0, 'FaceAlpha', .2);
text(1.2, 0.6, {"MSE = " + round(sum((1./(1+exp(-sigmoid.a*xs+sigmoid.b))-ys_sensitive).^2), 3)}, 'FontSize',10)
xlim([xs(1) xs(4)])
ylim([0 1])
set(gca,'XTick',[], 'FontSize',10)
title("High sensitivity")
hold off

% Sensitivity (insensitive example)
nexttile
ys_insensitive = [.3; .1; .8; .7]; % harley 04-26-2022
sigmoid = fit(xs,ys_insensitive,fittype('1/(1+exp(-a*x+b))'), 'StartPoint',[1; 0]);
conf = confint(sigmoid, .8);
scatter(xs, ys_insensitive, 100, 'k', 'filled')
hold on
fplot(1./(1+exp(-sigmoid.a*C+sigmoid.b)), 'k', 'LineWidth', 5)
a_low = 1./(1+exp(-conf(1,1)*xs_cont+sigmoid.b));
a_high = 1./(1+exp(-conf(2,1)*xs_cont+sigmoid.b));
x_range = [xs_cont, fliplr(xs_cont)];
a_inBetween = [a_low, fliplr(a_high)];
fill(x_range, a_inBetween, 'k', 'EdgeAlpha', 0, 'FaceAlpha', .2);
text(1.5, 0.3, {"MSE = " + round(sum((1./(1+exp(-sigmoid.a*xs+sigmoid.b))-ys_sensitive).^2), 3)}, 'FontSize',10)
xlim([xs(1) xs(4)])
ylim([0 1])
set(gca,'XTick',[], 'FontSize',10)
title("Low sensitivity")
hold off

xlabel(t, "incremented reward or cost, other fixed")
ylabel(t, "prob. approach")
t.TileSpacing = 'tight';