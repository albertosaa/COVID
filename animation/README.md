O código covid-anim.py gera os frames (114 no total) que dão origem a animação anim.gif

Há diversas maneiras de se gerar uma animação a partir das imagens dos seus frames. Neste caso em particular, cada frame está em um arquivo de nome fileNNN.gif, sendo NNN um inteiro que determina a ordem dos frames. Para se criar o gif no linux, basta usar o comando:

convert -delay 10  *.jpg anim.gif

