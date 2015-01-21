import board
import node
import random
import gui
import scrape
import Tkinter as tk
import time
import sys

#alphabet= ['A','E','O','S','T','I','M','N','P']
 
scrabble_val = {'A':1,'B':3,'C':3,'D':2,'E':1,'F':4,'G':2,'H':4,'I':1,
            'J':8,'K':5,'L':1, 'M':3,'N':1,'O':1,'P':3,'Q':10,'R': 1,
            'S': 1,'T': 1, 'U': 1, 'V': 4,'W': 4,'X': 8,'Y': 4,'Z':10}

class CSP:
  def __init__(self):
      self.across= {}
      self.down= {}
      self.allWords= {'a': self.across, 'd': self.down}
      self.needWords= []
      self.gotWords= []
      self.usedWords= []
      self.priorities = []

  def manual_join(self, char_arry):
    word = ""
    for i in char_arry:
      word += i
    return word


  def pick_optimal_word(self,node):
    min_word = None
    min_val = 9999999
    poss_words = [w for w in node.possibleWords if list(w) not in self.usedWords]
    #print "Possible words", poss_words, "done"
    for word in poss_words:
        scrabbleValues= [scrabble_val[word[i]] for i,inter in enumerate(node.intersections) if inter != None]
        if (sum(scrabbleValues) < min_val):
          rand = random.randint(1,20)
          if rand % 2 == 0 or min_word == None:
            min_word = word
            #print "\n\nMIN WORD=", min_word, "\n\n"
    self.usedWords += [list(min_word)]
    node.possibleWords.remove(min_word)
   # time.sleep(5)
    word = list(min_word)
    return word


  #direc: 'a'= across, 'd'=down
  def addNode(self, node, direc):
      if direc in ['a','d']:
      	self.allWords[direc][node.num]= node
      self.needWords += [(direc,node.num)]

  def getMaxLenWord(self):
    max_len = 0;
    max_word = None
    for direc, num in self.needWords:
      if max_len < len(self.allWords[direc][num].word):
        max_len = len(self.allWords[direc][num].word)
        max_word = (direc, num)
    return max_word


  def nextWord(self):
    ratios= []
    next_direc = None
    next_wordNum = None
    #print "Priorities lengths: ", len(self.priorities)
    if self.priorities != []:
      max_pri = 0
      for (direc, wordNum) in self.priorities:
        node = self.allWords[direc][wordNum]
        if node.priority > max_pri:
          max_pri = node.priority
          next_direc = direc
          next_wordNum = wordNum
    else:
      if (len(self.gotWords) < 11/2):
        next_direc, next_wordNum = self.getMaxLenWord()
      else:
        rand = random.randint(0,2)
        if rand ==2:
          next_direc, next_wordNum = self.getMaxLenWord()
        else:
          for (direc, wordNum) in self.needWords: 
            node= self.allWords[direc][wordNum]
            ratios += [((float(node.ratio[0])/float(node.ratio[1])+node.len/4),direc,wordNum)]
          #print ratios
          maxInds= [i for (i,val) in enumerate(ratios) if val[0]==max(ratios)[0]]
          if len(maxInds)>0:
            lengths= []
            for elem in maxInds:
              r,d,w= ratios[elem]
              node= self.allWords[d][w]
              lengths += [(node.len,d,w)]
            #print "NEXT if", max(lengths)[1], max(lengths)[2]
            next_direc, next_wordNum=  max(lengths)[1], max(lengths)[2]
          else:
            m= maxInds[0]
           # print "NEXT else", ratios[m][1], ratios[m][2]
            next_direc, next_wordNum =  ratios[m][1], ratios[m][2]
    #print "Next up: ", next_direc, next_wordNum, "Retries: ", self.allWords[next_direc][next_wordNum].num_retry
    return next_direc, next_wordNum



  def intersectionToChange(self,lst, opposite):
    lst= [(i,elem[0], elem[1]) for (i, elem) in enumerate(lst) if elem!=None]
    lengths= [(float(1)/float(self.allWords[opposite][num].len),j) for (j,(i,num,ind)) in enumerate(lst)]
    minLen,ind= min(lengths)
    return lst[ind]

  def get_opposite(self, direc):
    if direc == 'a':
        return 'd'
    else:
        return 'a'


  def backtrack(self, node, opposite, node_num):
    #print "IN BACK TRACK"
    node.priority += 1
    k, num, intPoint= self.intersectionToChange(node.intersections, opposite)
    problemNode= self.allWords[opposite][num]
    if (opposite,num) not in self.needWords: 
      self.priorities += [(opposite,num)]
    if problemNode.num_retry > 20 or len(problemNode.possibleWords) <= 1:
      opposite_par = self.get_opposite(opposite)
      k, num_par, intPoint= self.intersectionToChange(problemNode.intersections, opposite_par)
      problemNode_par= self.allWords[opposite_par][num_par]
      if problemNode_par.word in self.usedWords: 
        self.usedWords.remove(problemNode_par.word)
      if problemNode_par.word in problemNode_par.possibleWords:
        problemNode_par.possibleWords.remove(problemNode_par.word)
      problemNode_par.word= self.pick_optimal_word(problemNode_par)  #!!!!!
      if not ((opposite_par,num_par) in self.gotWords): 
         self.gotWords += [(opposite_par,num_par)]
      #print "Chose word", ''.join(problemNode_par.word), "for", opposite_par, num_par
      problemNode.priority = node.priority + 1
      self.priorities += [(opposite,num)]
      self.allWords[opposite_par][num_par].num_retry +=1
   #   self.allWords[opposite][num].priority = node.priority + 1
    else:
      #print "-------------Selected to backtrack on: ", opposite, num,"--------------"
      if problemNode.word in self.usedWords: 
        self.usedWords.remove(problemNode.word)
      current_word = ''.join(problemNode.word)
      #print "Current word: ", current_word
      #print problemNode.possibleWords
      #if problemNode.word in problemNode.possibleWords:
      if current_word in problemNode.possibleWords:
        #print "Remove current word"
        problemNode.possibleWords.remove(current_word)
      #print problemNode.possibleWords
      #print "Possible words list: ", len(problemNode.possibleWords)
      problemNode.word= self.pick_optimal_word(problemNode)  #!!!!!

      #print "Chose word", ''.join(problemNode.word), "for", opposite, num
      for ind,inter in enumerate(node.intersections):
        if inter!=None: 
          num,spot= inter
          interNode= self.allWords[opposite][num]
          interNode.addLetter(spot,node.word[ind])
      self.allWords[opposite][num].num_retry +=1
      if (opposite,num) in self.needWords:
        self.needWords.remove((opposite, num))
        self.priorities += [(self.get_opposite(opposite),node_num)]
  

  #just picks words randomly, no backtracking or anything
  #if a word gets filled up before being chosen, doesn't confirm whether it's actually a word (e.g. "AAG")

  #when picking intersection to change, maybe pick the one with fewest intersections ???
  #random letter selection must be smarter 
  #when picking word to set, pick one with largest unfilled:filled ratio 
  def solveCSP(self):
    print "Generating Crossword..."
    while(len(self.needWords)!=0):
      #print "\n\n\nNeedWords\n", self.needWords
      direc,wordNum= self.nextWord() #!!!!!
      opposite= 'd' if direc=='a' else 'a'
      node= self.allWords[direc][wordNum]
      if node.word==["?" for i in xrange(node.len)]:
        #index= random.randint(0,node.len-1)
        node.addLetter(i,random.choice(scrabble_val.keys()))
      query= ''.join(node.word)
      possibleWords= scrape.getPossibleWords(query)
      successful= True
      #print "Query: ", query, "possibleWords", possibleWords, "usedWords", self.usedWords
      if possibleWords==[]: 
        self.backtrack(node, opposite, wordNum)
        successful= False
      else: 
        #print possibleWords
        node.possibleWords= possibleWords
        node.word= self.pick_optimal_word(node)  #!!!!!
        #print "Chose word", ''.join(node.word), "for", direc, wordNum
        for ind,inter in enumerate(node.intersections):
          if inter!=None: 
            num,spot= inter
            interNode= self.allWords[opposite][num]
            interNode.addLetter(spot,node.word[ind])
      if successful:
        #print "Success for ", direc, wordNum
        if self.allWords[direc][wordNum].priority > 1:
          self.allWords[direc][wordNum].priority = 1
          self.priorities.remove((direc,wordNum))
        else:
          if (direc,wordNum) in self.needWords:
            self.needWords.remove((direc,wordNum))
        self.gotWords += [(direc,wordNum)]
    print "Crossword complete! Creating GUI..."

#Invariants: 
# 1) All w that have children, have been populated such that they satisfy their parents and grandparents 
# 2) If w is a problem node, first backtrack to its parents, then to its siblings


    
  def printWordsToGui(self,board):
    for direc,wordNum in self.gotWords:
      node= self.allWords[direc][wordNum]
      xCoord= node.coords[0]
      yCoord= node.coords[1]
      #print node.word
      if direc=='a':
        board.acrossClues[wordNum]= scrape.getClue(''.join(map(str, node.word)))
        for i in range(node.len):
          board.solution[xCoord][yCoord+i]= node.word[i]
      else: 
        board.downClues[wordNum]= scrape.getClue(''.join(map(str, node.word)))
        for i in range(node.len):
          board.solution[xCoord+i][yCoord]= node.word[i]
    '''for row in board.solution: 
      print row'''

    
def main():
    size= 11
    cross= board.Board(size)
    csp_cross= CSP()
    #define board

    #11 by 11 1st version
    cross.board[2][4] = None
    cross.board[2][5] = None
    cross.board[3][6] = None

    cross.board[0][5] = None
    cross.board[0][6] = None
    cross.board[0][7] = None
    cross.board[0][8] = None
    cross.board[0][9] = None
    cross.board[1][0] = None
    cross.board[1][2] = None
    cross.board[1][3] = None
    cross.board[1][4] = None
    cross.board[2][0] = None
    cross.board[2][7] = None
    cross.board[2][8] = None
    cross.board[2][9] = None
    cross.board[2][10] = None
    cross.board[3][0] = None
    cross.board[3][2] = None
    cross.board[4][0] = None
    cross.board[4][2] = None
    cross.board[4][6] = None
    cross.board[4][7] = None
    cross.board[4][8] = None
    cross.board[4][9] = None
    cross.board[5][0] = None
    cross.board[5][2] = None
    cross.board[5][5] = None
    cross.board[5][8] = None
    cross.board[5][10] = None
    cross.board[6][1] = None
    cross.board[6][2] = None
    cross.board[6][3] = None
    cross.board[6][4] = None
    cross.board[6][8] = None
    cross.board[6][10] = None
    cross.board[7][8] = None
    cross.board[7][10] = None
    cross.board[8][0] = None
    cross.board[8][1] = None
    cross.board[8][2] = None
    cross.board[8][3] = None
    cross.board[8][10] = None
    cross.board[9][6] = None
    cross.board[9][7] = None
    cross.board[9][8] = None
    cross.board[9][10] = None
    cross.board[10][1] = None
    cross.board[10][2] = None
    cross.board[10][3] = None
    cross.board[10][4] = None
    cross.board[10][5] = None
    cross.board[4][4] = None
    cross.board[5][4] = None
    cross.board[4][4] = None
    cross.board[5][4] = None
    cross.board[5][6] = None
    cross.board[6][6] = None

    cross.board[7][4] = None
    cross.board[8][5] = None
    cross.board[8][6] = None

    #print cross.board
    cross.genWordsFromBoard(csp_cross)
    cross.setWordNumbers(csp_cross)
    cross.calcIntersections(csp_cross)

    #print "Solving CSP:"
    csp_cross.solveCSP()
    csp_cross.printWordsToGui(cross)


#GUI STUFF
    boardMult= {11:65, 15:50, 25:40} 
    clueMult= {11:5, 15:4, 25:3}
    numFontSize= {11:21, 15:18, 25:16}
    letterFontSize= {11:32, 15:28, 25:24}
    root = tk.Tk()
    root.resizable(False, False)
    leftFrame= tk.Frame(root)
    rightFrame= tk.Frame(root)
    gameboard = gui.GameBoard(leftFrame, cross, cross.solution, boardMult[size]*size, numFontSize[size], letterFontSize[size])
    clues= gui.Clues(rightFrame, cross.acrossClues, cross.downClues, clueMult[size]*size)

    leftFrame.pack(side="left")
    rightFrame.pack(side="right")
    gameboard.canvas.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    clues.text.pack(side="right")
    root.mainloop()
    
if __name__=="__main__":
      main()