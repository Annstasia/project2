# project2
В игре 'семь' в распоряжении игрока находятся 7 фигур: 1 король, 2 аристократа, 4 солдата. Такой же состав команды у компьютера. 

Король атакует аристократа и короля

Аристократ – простолюдина и аристократа

Простолюдин – короля и простолюдина

В начале игры задаётся порядок атаки и диапазон отступления для каждой фигуры. Согласно заданному порядку фигуры двигаются в течение 
12 следующих раундов. Одной из фигур управляет игрок, сменить ведомую фигуру можно при помощи клавиши пробела.

За уничтожение короля противника прибавляется 800 баллов(за потерю своего – вычитается). Аналогично для аристократа – 400 баллов, для 
простолюдина – 200 баллов

По прохождении 12 раундов, баллы за каждый раунд суммируются. Если игрок ушел в плюс, то он переходит на следующий уровень
Цель игры – набрать как можно больше баллов за 12 раундов
За баллы можно преорести новые скины

ВАЖНО
В папках с скинами(4 - 17) хранятся только изображения "родителей". Перед запуском основной программы стоит запустить rewriteImage.py
После этого в папках появятся изображения для фигур