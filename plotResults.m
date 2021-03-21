close all;
clear all;

data = load('output.txt');
states = data(:, 1); 
actions = data(:, 2);
ns_app = data(:,3);
we_app = data(:,4);
rewards  = data(:,5);

ns = ns_app;
we = we_app;
saStat = zeros(25,9);
sStat = zeros(25,1);
for i = 1:25
	I = find(states==(i-1));
	saStat(i,:) = [sum(actions(I)==0), sum(actions(I)==1), sum(actions(I)==2),sum(actions(I)==3), sum(actions(I)==4), sum(actions(I)==5),sum(actions(I)==6), sum(actions(I)==7), sum(actions(I)==8)];
  sStat(i) = length(I);
end

%dim = [.85 .45 .3 .3];
% str = {'1 LL', '2 LM','3 ML','4 MM','5 LH','6 HL','7 MH','8 HM','9 HH'};
% 
% % State-action statistics
% f = figure(1)
% bar(saStat,'grouped')
% t = title('State-action statistics');
% h = legend('a (0,0)', 'a (+dt, -dt)', 'a (-dt, +dt)');
% x = xlabel('States');
% y = ylabel('Number of occurence');
% a = annotation('textbox',dim,'String',str,'FitBoxToText','on');
% grid on
% set(t, 'fontsize', 20);
% set(h, 'fontsize', 20);
% set(x, 'fontsize', 20);
% set(y, 'fontsize', 20);
% set(a, 'fontsize', 20);
% 
% State statistics
figure(2)
bar(sStat, 'stacked')
t = title('State statistics');
x = xlabel('States');
y = ylabel('Number of occurence');
%grid on
set(t, 'fontsize', 10);
%set(h, 'fontsize', 20);
set(x, 'fontsize', 10);
set(y, 'fontsize', 10);
%set(a, 'fontsize', 20);

% 
% 
% % NS number of halting cars statistics
% figure(3)
% bar(ns, 'stacked')
% t = title('North-South number of halting cars');
% x = xlabel('Cycle index');
% y = ylabel('NS number of halting vehicles');
% grid on
% set(t, 'fontsize', 20);
% set(x, 'fontsize', 20);
% set(y, 'fontsize', 20);
% 
% 
% % NS number of halting cars statistics
% figure(4)
% bar(we, 'stacked')
% t = title('West-East number of halting cars');
% x = xlabel('Cycle index');
% y = ylabel('WE number of halting vehicles');
% grid on
% set(t, 'fontsize', 20);
% set(x, 'fontsize', 20);
% set(y, 'fontsize', 20);
% 
% State statistics
figure(5)
bar(states(:)+1, 'stacked')
t = title('State occurence');
x = xlabel('Cycle index');
y = ylabel('State');
%a = annotation('textbox',dim,'String',str,'FitBoxToText','on');
set(t, 'fontsize', 10);
set(x, 'fontsize', 10);
set(y, 'fontsize', 10);
%set(a, 'fontsize', 20);
% 
% WE, NS number of halting cars statistics
f = figure(6);
bar([ns, we],'grouped')
t = title('North-South and West-East number of halting cars');
h = legend('NS', 'WE');
x = xlabel('Cycle index');
y = ylabel('Number of halting vehicles');
%a = annotation('textbox',dim,'String',str,'FitBoxToText','on');
grid on
set(t, 'fontsize', 10);
set(h, 'fontsize', 10);
set(x, 'fontsize', 10);
set(y, 'fontsize', 10);
%set(a, 'fontsize', 20);

% Rewards
figure(7)
bar(rewards, 'stacked')
t = title('Reward evolution');
x = xlabel('Cycle index');
y = ylabel('Reward');
grid on
set(t, 'fontsize', 10);
set(x, 'fontsize', 10);
set(y, 'fontsize', 10);


% %% Comparison of state statistics
% data1 = load('output_experiment1.txt');
% states1 = data1(:, 1); 
% data2 = load('output_experiment2.txt');
% states2 = data2(:, 1); 
% %
% %sStat1 = zeros(9,1);
% %sStat2 = zeros(9,1);
% %for i = 1:9
% %	I1 = find(states1==(i-1));
% %	sStat1(i) = length(I1);
% %  I2 = find(states2==(i-1));
% %	sStat2(i) = length(I2);
% %end
% %
% figure(7)
% bar([states1+1, states2+1, states+1],'grouped')
% h = legend('Fixed sym', 'Fixed asym', 'Adopted');
% %bar([states1+1, states+1],'grouped')
% %h = legend('Fixed sym', 'Adapted');
% t = title('Comparison of experiments');
% x = xlabel('Cycle index');
% y = ylabel('States');
% a = annotation('textbox',dim,'String',str,'FitBoxToText','on');
% set(t, 'fontsize', 20);
% set(h, 'fontsize', 20);
% set(x, 'fontsize', 20);
% set(y, 'fontsize', 20);
% set(a, 'fontsize', 20);
