function TSEvent(event_type,message,file)

text1 = datestr(now,'HH:MM:SS.FFF')+" - ";
text2 = "EVENT TYPE: '"+event_type+"' "+message+"\n";

msg = text1+text2;

evlogid = fopen(file,'a');
fprintf(evlogid,msg);
fclose(evlogid);

end