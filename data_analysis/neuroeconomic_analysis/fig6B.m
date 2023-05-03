cost_levels = 1/4:1/4:1;
reward_levels = 1/4:1/4:1;

% fake data to illustrate
observed_p_appr = zeros(4);
rs = repelem(reward_levels,1,length(reward_levels))';
cs = repmat(cost_levels,1,length(cost_levels))';
ps = zeros(length(cost_levels)*length(reward_levels),1);

i = 1;
for r=1:length(reward_levels)
    for c=1:length(cost_levels)
        ps(i) = 1./(1+exp(-2*r+3))*1./(1+exp(.6*c-2));
        observed_p_appr(c,r) = ps(i);
        i = i+1;
    end
end

syms R C

g = fittype( @(a_R,b_R,a_C,b_C,R,C) 1./(1+exp(-a_R.*R+b_R))*1./(1+exp(a_C.*C+b_C)), ...
        'coefficients', {'a_R','b_R','a_C','b_C'}, 'independent', {'R', 'C'}, ...
        'dependent', 'z' );

% Call fit and specify the value of c.
f = fit( [rs, cs], ps, g, 'StartPoint', [1; 0; 1; 0] );

fsurf(@(R,C) 1./(1+exp(-f.a_R.*R+f.b_R))*1./(1+exp(f.a_C.*C+f.b_C)), [0, 1])
frc = 1/(1+exp(-f.a_R*R+f.b_R))*1/(1+exp(f.a_C*C+f.b_C));
boundary_line = solve(frc==.5, C);


B = tiledlayout(1,2);

% Normal
nexttile
imagesc(observed_p_appr);
cMap = [interp1(0:1,[0.64 0.08 0.18; 1 1 1],linspace(0,1,100)); ones([100,3]); interp1(0:1,[1 1 1; 0.47 0.67 0.19],linspace(0,1,100))];
colormap(cMap);
cb = colorbar;
cb.Ticks = [0 0.5 1];
caxis([0 1]);
hold on
x_cont_prelim = linspace(0, 1.5, 1000);
dashed_curve_prelim = subs(boundary_line, R, x_cont_prelim)*4;
x_cont = x_cont_prelim(imag(dashed_curve_prelim)==0);
dashed_curve = dashed_curve_prelim(imag(dashed_curve_prelim)==0);
plot(x_cont*4, dashed_curve, '--k', 'LineWidth',5)
ylabel(cb,'approach rate')
set(gca,'xtick',[], 'ytick',[], 'FontSize',20, 'YDir','normal');
xlabel('reward')
ylabel('cost')
title("3D Psychometric fun.")
hold off

% Pyschometric function derivation
nexttile
scatter(reward_levels', observed_p_appr(3,:)', 100, 'k', 'filled')
hold on
fplot(1./(1+exp(-f.a_R.*R+f.b_R))*1./(1+exp(f.a_C.*cost_levels(3)+f.b_C)), 'k', 'LineWidth', 5)
fplot(.5, '--k', 'LineWidth', 5)
title("2D reward slices")
set(gca,'XTick',[], 'FontSize',20)
xlabel("reward")
xlim([0 1])
ylim([0 1])
hold off