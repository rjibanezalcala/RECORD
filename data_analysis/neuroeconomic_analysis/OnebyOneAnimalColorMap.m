% AnimalList = {'aladdin', 'jimi', 'mike', 'sarah', 'simba'};
% AnimalList = {'fiona', 'jafar', 'juana', 'raissa', 'sully'};
datasource = 'live_database'; %ENTER YOUR DATASOURCE NAME HERE, default should be "live_database"
username = 'postgres'; %ENTER YOUR USERNAME HERE, default should be "postgres"
password = '1234'; %ENTER YOUR PASSWORD HERE, default should be "1234"
conn = database(datasource,username,password); %creates the database connection
query = "SELECT intensityofcost1, intensityofcost3, subjectid FROM live_table;";
results= fetch(conn,query);

AnimalList = unique(results.subjectid);
LuxList = unique(results.intensityofcost3);

n = length(AnimalList);
l = length(LuxList);

i = 1;

LuxList1Num = zeros(1,1); 
LuxList1Num(1) = 15;


LuxList = LuxList(2:(l-6));
l2 = length(LuxList);
LuxListNum = zeros(l2,1);
for b = 1:l2
    str = LuxList(b);
    str2 = extractBetween(str, 1,3);
    num = str2num(string(str2));
    LuxListNum(b) = num;
end

joinedLuxList = cat(1,LuxList1Num, LuxListNum);

disp(joinedLuxList);
% for a = 1:n
%     foldername = "ColorPlots/" + AnimalList(a);
%     mkdir(foldername);
% end




            query2a = "SELECT approachavoid FROM live_table WHERE tasktypedone = 'P2 L1' AND health = 'N/A' AND subjectid = '" + AnimalList(i)+ "' AND feeder = '1' AND lightlevel = '1';";
            res2a = fetch(conn,query2a);

            query2b = "SELECT approachavoid FROM live_table WHERE tasktypedone = 'P2 L1' AND health = 'N/A' AND subjectid = '" + AnimalList(i)+ "' AND feeder = '2' AND lightlevel = '1';";
            res2b = fetch(conn,query2b);
            
            query2c = "SELECT approachavoid FROM live_table WHERE tasktypedone = 'P2 L1' AND health = 'N/A' AND subjectid = '" + AnimalList(i)+ "' AND feeder = '3' AND lightlevel = '1';";
            res2c = fetch(conn,query2c);

            query2d = "SELECT approachavoid FROM live_table WHERE tasktypedone = 'P2 L1' AND health = 'N/A' AND subjectid = '" + AnimalList(i)+ "' AND feeder = '4' AND lightlevel = '1';";
            res2d = fetch(conn,query2d);

        AcceptancePercent2a = zeros(1,1);
        AcceptanceVector2a = str2double(res2a.approachavoid);
        AcceptanceVector2a = AcceptanceVector2a(~isnan(AcceptanceVector2a));
        len2a= length(AcceptanceVector2a);
        S2a= sum(AcceptanceVector2a);
        AcceptancePercent2a(1) = (S2a/len2a);

        AcceptancePercent2b = zeros(1,1);
        AcceptanceVector2b = str2double(res2b.approachavoid);
        AcceptanceVector2b = AcceptanceVector2b(~isnan(AcceptanceVector2b));
        len2b= length(AcceptanceVector2b);
        S2b= sum(AcceptanceVector2b);
        AcceptancePercent2b(1) = (S2b/len2b);

        AcceptancePercent2c = zeros(1,1);
        AcceptanceVector2c = str2double(res2c.approachavoid);
        AcceptanceVector2c = AcceptanceVector2c(~isnan(AcceptanceVector2c));
        len2c= length(AcceptanceVector2c);
        S2c= sum(AcceptanceVector2c);
        AcceptancePercent2c(1) = (S2c/len2c);

        AcceptancePercent2d = zeros(1,1);
        AcceptanceVector2d = str2double(res2d.approachavoid);
        AcceptanceVector2d = AcceptanceVector2d(~isnan(AcceptanceVector2d));
        len2d= length(AcceptanceVector2d);
        S2d= sum(AcceptanceVector2d);
        AcceptancePercent2d(1) = (S2d/len2d);
   

        for k = 1:l2
            query1a = "SELECT approachavoid FROM live_table WHERE tasktypedone = 'P2 L1L3' AND intensityofcost3 = '" + LuxList(k) + "' AND health = 'N/A' AND subjectid = '" + AnimalList(i)+ "' AND feeder = '1' AND lightlevel = '1';";
            res1a = fetch(conn,query1a);

            query1b = "SELECT approachavoid FROM live_table WHERE tasktypedone = 'P2 L1L3' AND intensityofcost3 = '" + LuxList(k) + "' AND health = 'N/A' AND subjectid = '" + AnimalList(i)+ "' AND feeder = '2' AND lightlevel = '1';";
            res1b = fetch(conn,query1b);
            
            query1c = "SELECT approachavoid FROM live_table WHERE tasktypedone = 'P2 L1L3' AND intensityofcost3 = '" + LuxList(k) + "' AND health = 'N/A' AND subjectid = '" + AnimalList(i)+ "' AND feeder = '3' AND lightlevel = '1';";
            res1c = fetch(conn,query1c);

            query1d = "SELECT approachavoid FROM live_table WHERE tasktypedone = 'P2 L1L3' AND intensityofcost3 = '" + LuxList(k) + "' AND health = 'N/A' AND subjectid = '" + AnimalList(i)+ "' AND feeder = '4' AND lightlevel = '1';";
            res1d = fetch(conn,query1d);
    
        AcceptanceVector1a = str2double(res1a.approachavoid);
        AcceptanceVector1a = AcceptanceVector1a(~isnan(AcceptanceVector1a));
        l1a= length(AcceptanceVector1a);
        S1a= sum(AcceptanceVector1a);
        AcceptancePercent1a(k) = (S1a/l1a);

        AcceptanceVector1b = str2double(res1b.approachavoid);
        AcceptanceVector1b = AcceptanceVector1b(~isnan(AcceptanceVector1b));
        l1b= length(AcceptanceVector1b);
        S1b= sum(AcceptanceVector1b);
        AcceptancePercent1b(k) = (S1b/l1b);

        AcceptanceVector1c = str2double(res1c.approachavoid);
        AcceptanceVector1c = AcceptanceVector1c(~isnan(AcceptanceVector1c));
        l1c= length(AcceptanceVector1c);
        S1c= sum(AcceptanceVector1c);
        AcceptancePercent1c(k) = (S1c/l1c);

        AcceptanceVector1d = str2double(res1d.approachavoid);
        AcceptanceVector1d = AcceptanceVector1d(~isnan(AcceptanceVector1d));
        l1d= length(AcceptanceVector1d);
        S1d= sum(AcceptanceVector1d);
        AcceptancePercent1d(k) = (S1d/l1d);

        end 

%        disp(AcceptancePercent2);

        joinedAccPerd = cat(2,AcceptancePercent2d, AcceptancePercent1d);
        bin1d = joinedAccPerd(2:5);
        bin1entryd = mean(bin1d, 'omitnan');
        bin2d =  joinedAccPerd(6:11);
        bin2entryd = mean(bin2d, 'omitnan');
        bin3d = joinedAccPerd(12:15);
        bin3entryd = mean(bin3d, 'omitnan');
        
       
        joinedAccPerc = cat(2,AcceptancePercent2c, AcceptancePercent1c);
        bin1c = joinedAccPerc(2:5);
        bin1entryc = mean(bin1c, 'omitnan');
        bin2c =  joinedAccPerc(6:11);
        bin2entryc = mean(bin2c, 'omitnan');
        bin3c = joinedAccPerc(12:15);
        bin3entryc = mean(bin3c, 'omitnan');
        
        joinedAccPerb = cat(2,AcceptancePercent2b, AcceptancePercent1b);
        bin1b = joinedAccPerb(2:5);
        bin1entryb = mean(bin1b, 'omitnan');
        bin2b =  joinedAccPerb(6:11);
        bin2entryb = mean(bin2b, 'omitnan');
        bin3b = joinedAccPerb(12:15);
        bin3entryb = mean(bin3b, 'omitnan');

        joinedAccPera = cat(2,AcceptancePercent2a, AcceptancePercent1a);
        bin1a = joinedAccPera(2:5);
        bin1entrya = mean(bin1a, 'omitnan');
        bin2a =  joinedAccPera(6:11);
        bin2entrya = mean(bin2a, 'omitnan');
        bin3a = joinedAccPera(12:15);
        bin3entrya = mean(bin3a, 'omitnan');

Z = zeros(4,4);

Z(1,1) = AcceptancePercent2d(1);
Z(2,1) = AcceptancePercent2c(1);
Z(3,1) = AcceptancePercent2b(1);
Z(4,1) = AcceptancePercent2a(1);

Z(1,2) = bin1entryd;
Z(2,2) = bin1entryc;
Z(3,2) = bin1entryb;
Z(4,2) = bin1entrya;

Z(1,3) = bin2entryd;
Z(2,3) = bin2entryc;
Z(3,3) = bin2entryb;
Z(4,3) = bin2entrya;

Z(1,4) = bin3entryd;
Z(2,4) = bin3entryc;
Z(3,4) = bin3entryb;
Z(4,4) = bin3entrya;

disp(Z)
Out = transpose(Z);

%% Modeling & Plotting

cost_levels = 1/4:1/4:1;
reward_levels = 1/4:1/4:1;

% fake data to illustrate
rs = repelem(reward_levels,1,length(reward_levels))';
cs = repmat(cost_levels,1,length(cost_levels))';
ps = zeros(length(cost_levels)*length(reward_levels),1);

i = 1;
for r=1:length(reward_levels)
    for c=1:length(cost_levels)
        ps(i) = Out(c,r);
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

% Plotting
nexttile
imagesc(observed_p_appr);
cMap = [interp1(0:1,[0.64 0.08 0.18; 1 1 1],linspace(0,1,100)); ones([100,3]); interp1(0:1,[1 1 1; 0.47 0.67 0.19],linspace(0,1,100))];
colormap(cMap);
cb = colorbar;
cb.Ticks = [0 0.5 1];
clim([0 1]);
hold on
x_cont_prelim = linspace(0, 1.5, 1000);
dashed_curve_prelim = subs(boundary_line, R, x_cont_prelim)*4;
x_cont = x_cont_prelim(imag(dashed_curve_prelim)==0);
dashed_curve = dashed_curve_prelim(imag(dashed_curve_prelim)==0);
plot(x_cont*4, dashed_curve, ':k', 'LineWidth',5)
rectangle('Position',[0.5 1.5 4.0 1], 'LineWidth',5)
ylabel(cb,'approach rate')
set(gca,'xtick',[], 'ytick',[], 'FontSize',20, 'YDir','normal');
xlabel('reward')
ylabel('cost')
title("3D Psychometric fun.")
hold off

% psychometric functions
nexttile
for rew=1:4
    R_ = rs(rew);
    scatter(Out(:,rew),'filled')
    fplot(1./(1+exp(-f.a_R.*R_+f.b_R))*1./(1+exp(f.a_C.*C+f.b_C)))
end
for cost=1:4
    C_ = cs(cost);
    scatter(Out(cost,:),'filled')
    fplot(1./(1+exp(-f.a_R.*R+f.b_R))*1./(1+exp(f.a_C.*C_+f.b_C)))
end