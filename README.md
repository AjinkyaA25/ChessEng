This Chess engine does a basic analysis of the position and will return the best move based on its evaluation. To get the correct evaluation, I have implemented a alpha beta pruning algorithm which should
speed up the time that it takes to analyze the position. Furthermore, my engine will analyze all moves except for promotions to a non queen piece as it is very rarely the best move.
This project allows 2 players to play against each other or 2 AIs to play against each other depending on the variable values of PlayerOne and PlayerTwo. If the values of PlayerOne or PlayerTwo are false, 
it will assume an AI to take over, but if they are true, then it will allow players to make moves.
By simply changing the values of these players, you can play against a friend or even play against the AI or even make the AIs play each other. 
