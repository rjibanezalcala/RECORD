function TSEndLog(message,file)

text1 = "\n"+datestr(now,'dd-mm-yy')+"\n";
text2 = datestr(now,'HH:MM:SS.FFF')+" - ";
text3 = "LOG END "+message+"\n\n";

msg = text1+text2+text3;

evlogid = fopen(file,'a');
fprintf(evlogid,msg);
fclose(evlogid);

end