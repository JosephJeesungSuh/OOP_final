from PIL import Image
from math import *
import tkinter as tk
import time

dark = 87
eps = 10
eps2 = 7.0
eps3 = 10.0
pi = 3.14159265358979
trytime = 100
minimumlimit = 20
wordtable = [(100000,"a"),(101000,"b"),(110000,"c"),(110100,"d"),(100100,"e"),(111000,"f"),(111100,"g"),(101100,"h"),
             (11000,"i"),(11100,"j"),(100010,"k"),(101010,"l"),(110010,"m"),(110110,"n"),(100110,"o"),(111010,"p"),
             (111110,"q"),(101110,"r"),(11010,"s"),(11110,"t"),(100011,"u"),(101011,"v"),(110011,"x"),(110111,"y"),
             (100111,"z"),(11101,"w"),(1000,","),(1010,";"),(1100,":"),(1101,"."),(1110,"!"),(1111,"("),(1011,"?"),
             (110,"*"),(10,"'"),(11,"-"),(1,"`"),(10111,"~")]

def dist(a,b,c,d,e) :
    return abs(a*d+b*e+c)/sqrt(a*a+b*b)

def tych(a) :
    return a[0] + a[1] + a[2]

def getkey(item) :
    return item[0]

class Messenger:
    def __init__(self,getText) :
        self.txt = getText
        try :
            self.im = Image.open(self.txt)
        except:
            self.im = False
        self.direction = [[0,1],[0,-1],[1,0],[-1,0]]
        self.lx = 0
        self.ly = 0
        self.rx = 0
        self.ry = 0
        self.listofpoint = []
        self.paint = 0
        self.output = ""
    
    def start(self) :
        self.time = time.time()
        self.im = self.im.convert("RGB")
        size = self.im.size
        self.width = size[0]
        self.height = size[1]
        self.visit = [[0]*self.height for i in range(self.width)]
        self.makeRGB()
        self.process_ocr()
        self.refine()
        self.cutline()
        self.transform()
        self.lineseg()
        self.detail()
        return self.encrypt()
        
    def process_ocr(self) :
        print("process_ocr")
        for i in range(0,self.width) :
            for j in range(0,self.height) :
                if self.visit[i][j] : continue
                if self.getRGB(i,j) < dark :
                    self.paint += 1
                    self.lx = self.width-1
                    self.ly = self.height-1
                    self.rx = self.ry = 0
                    queue = []
                    self.visit[i][j] = self.paint
                    queue.append((i,j))
                    while(len(queue)) :
                        now = queue[0]
                        queue.pop(0)
                        self.circleupdate(now[0], now[1])
                        for d in self.direction :
                            nxt = now[0] + d[0]
                            nyt = now[1] + d[1]
                            if nxt >= self.width or nxt < 0 or nyt >= self.height or nyt < 0 or self.visit[nxt][nyt] :
                                continue
                            if self.getRGB(nxt,nyt) < dark:
                                self.visit[nxt][nyt] = self.paint
                                queue.append((nxt,nyt))
                    self.listofpoint.append([self.paint,self.lx,self.ly,self.rx,self.ry])
        self.iscircle()

    def circleupdate(self,x,y) :
        self.lx = min(self.lx, x)
        self.ly = min(self.ly, y)
        self.rx = max(self.rx, x)
        self.ry = max(self.ry, y)

    def iscircle(self) :
        print("iscircle")
        eraselist = []
        for i in self.listofpoint :
            ratio = (i[3]-i[1]+1) / (i[4]-i[2]+1)
            if ratio > 1.5 or ratio < 0.67 : eraselist.append(i)
            elif i[3]-i[1] > 50 : eraselist.append(i)
            else :
                cnt = 0
                for x in range(i[1],i[3]+1) :
                    for y in range(i[2],i[4]+1) :
                       cnt += (int)(self.getRGB(x,y) < dark)
                if cnt/(i[3]-i[1]+1)/(i[4]-i[2]+1) < 0.5 : eraselist.append(i)
        for i in eraselist :
            self.listofpoint.remove(i)

    def refine(self) :
        print("refine")
        refined = []
        for i in self.listofpoint :
            cx = (i[3]+i[1])/2
            cy = (i[4]+i[2])/2
            refined.append((cx-self.width/2,cy-self.height/2))
        keeperase = True
        while keeperase :
            leng = len(refined)
            keeperase = False
            for i in range(0,leng) :
                if keeperase :
                    break
                for j in range(0,i) :
                    if keeperase :
                        break
                    if abs(refined[i][0]-refined[j][0])+abs(refined[i][1]-refined[j][1]) < eps2 :
                        refined.remove(refined[j])
                        keeperase = True
        self.listofpoint = refined

    def cutline(self):
        print("cutline")
        cutting = 2*pi
        trytime = self.height//6
        for degree in range(0,179) :
            if cutting != 2*pi : break
            for yth in range(-trytime,trytime) :
                a = tan(degree*pi/360)
                b = 1/cos(degree*2*pi/360) * yth
                if b>self.height/2 : break
                cnt = 0
                for i in self.listofpoint :
                    cnt += (int)(dist(a,-1,b,i[0],i[1]) < eps)
                if cnt == 0 :
                    cutting = degree*pi/360
                    break
                a = tan(-degree*pi/360)
                b = 1/cos(-degree*pi/360) * yth
                cnt = 0
                for i in self.listofpoint :
                    cnt += (int)(dist(a,-1,b,i[0],i[1]) < eps)
                if cnt == 0 :
                    cutting = -degree*pi/360
                    break
        self.cutting = cutting

    def transform(self) :
        print("transform")
        sine = sin(-self.cutting)
        cose = cos(-self.cutting)
        refined = []
        for i in self.listofpoint :
            cx = i[0]*cose-i[1]*sine
            cy = i[0]*sine+i[1]*cose
            refined.append((cx,cy))
        self.listofpoint = refined

    def lineseg(self) :
        print("lineseg")
        visit = [False] * len(self.listofpoint)
        refined = []
        yth = self.height//2+(int)(eps2)
        collector = False
        while yth >= -self.height//2-(int)(eps2) :
            cnt = 0
            for i in self.listofpoint :
                cnt += (int)(abs(yth-i[1]) < eps)
            if collector :
                if cnt == 0 :
                    ret = []
                    for i in range(0,len(self.listofpoint)) :
                        if visit[i] : continue
                        if self.listofpoint[i][1] > yth :
                            visit[i] = True
                            ret.append(self.listofpoint[i])
                    refined.append(ret)
                    collector = False
            else :
                if cnt : collector = True
            yth -= 2
        self.listofpoint = refined

    def detail(self) :
        print("detail")
        unit = 0
        unit2 = 0
        for i in self.listofpoint :
            if len(i) < minimumlimit :
                continue
            distset = []
            for j in range(0,len(i)) :
                for k in range(0,j) :
                    distset.append(abs(i[j][0]-i[k][0]))
            distset.sort()
            while len(distset) > 0 and distset[0] < eps2 : distset.pop(0)
            it = 0
            while it+2 < len(distset) and abs(distset[it]+distset[it+2]-2*distset[it+1]) < eps2 : it += 1
            unit_ = 0
            for j in range(0,min(it+2,len(distset))) : unit_ += distset[j]
            unit += unit_/(it+2)
            it += 2
            itcopy = it
            while it+2 < len(distset) and abs(distset[it]+distset[it+2]-2*distset[it+1]) < eps2 : it += 1
            unit_ = 0
            for j in range(itcopy,min(it+2,len(distset))) : unit_ += distset[j]
            unit2 += unit_/(it+2-itcopy)
        unit = unit / len(self.listofpoint)
        self.unit = unit
        unit2 = unit2 / len(self.listofpoint)
        self.unit2 = unit2
        
        xset = []
        for i in self.listofpoint :
            for j in i :
                xset.append(j[0])
        xset.sort()
        it = 0
        it2 = len(xset)-1
        while it+2 < len(distset) and abs(xset[it] + xset[it+2] - 2*xset[it+1]) < eps2 : it += 1
        while it2-2 >= 0 and abs(xset[it2] + xset[it2-2] - 2*xset[it2-1]) < eps2 : it2 -= 1
        xmin = 0
        xmax = 0
        for i in range(0,min(it+2,len(distset))) : xmin += xset[i]
        for i in range(max(0,it2-1),len(xset)) : xmax += xset[i]
        xmin = xmin / (it+2)
        xmax = xmax / (len(xset)-it2+1)
        self.xmin = xmin
        self.xmax = xmax

        self.listofpoint.reverse()
        for i in self.listofpoint :
            if len(i) < minimumlimit :
                continue
            yset = []
            for j in range(0,len(i)) : yset.append(i[j][1])
            yset.sort()
            it = 0
            while it+2 < len(yset) and abs(yset[it]+yset[it+2]-2*yset[it+1] < eps2) : it += 1
            itcopy = it + 2
            it += 2
            while it+2 < len(yset) and abs(yset[it]+yset[it+2]-2*yset[it+1]) < eps2 : it += 1
            itcopy2 = it + 2
            y1 = 0
            y2 = 0
            y3 = 0
            for j in range(0,itcopy) : y1 += yset[j]
            for j in range(itcopy,itcopy2) : y2 += yset[j]
            for j in range(itcopy2,len(yset)) : y3 += yset[j]
            if itcopy : y1 /= itcopy
            if itcopy2-itcopy : y2 /= itcopy2-itcopy
            if len(yset)-itcopy2 : y3 /= len(yset)-itcopy2
            pt = i
            pt.sort(key=getkey)
            front = 0
            rear = 0
            while front < len(pt) :
                while rear < len(pt)-1 and abs(pt[rear][0]-pt[rear+1][0]) < unit + eps2 :
                    rear += 1
                letter = self.makeletter(pt[front:rear+1],y1,y2,y3)
                self.output += letter
                front = rear + 1
                if front < len(pt) and pt[front][0]-pt[rear][0] > unit+2*unit2-eps2 :
                    self.output += " "
                rear = front
            if xmax-pt[len(pt)-1][0] > unit2 + unit + eps3:
                self.output += " "

    def makeletter(self,arr,y1,y2,y3) :
        dot = [[0] * 2 for i in range(3)]
        if self.oneline(arr) :
            for i in arr :
                if abs(i[1]-y1) < eps3 : dot[0][0] = True
                elif abs(i[1]-y2) < eps3 : dot[1][0] = True
                elif abs(i[1]-y3) < eps3 : dot[2][0] = True
        else :
            cut = 0
            while cut+1 < len(arr) and arr[cut+1][0] - arr[cut][0] < eps2 : cut += 1
            for i in range(len(arr)):
                if abs(arr[i][1]-y1) < eps3 : dot[0][i>cut] = True
                elif abs(arr[i][1]-y2) < eps3 : dot[1][i>cut] = True
                elif abs(arr[i][1]-y3) < eps3 : dot[2][i>cut] = True
        hash = 0
        for i in range(0,3) :
            for j in range(0,2) :
                hash = 10*hash + dot[i][j]
        for i in wordtable :
            if hash == i[0] :
                return i[1]
        return "???"

    def encrypt(self) :
        for i in range(0,len(self.output)-1) :
            if self.output[i] == "'" and self.output[i+1] != "'" :
                self.output = self.output[:i]+"`"+self.output[i+1:]
        for i in range(26) :
            exchange = "`"+wordtable[i][1]
            self.output = self.output.replace(exchange,wordtable[i][1].upper())
            self.output = self.output.replace(" "+wordtable[i][1].upper(),"\n"+wordtable[i][1].upper())
        return self.output + "\n\nIt took "+ str(round(10*(time.time()-self.time))/10) +" seconds for translation."

    def oneline(self,arr) :
        for i in range(0,len(arr)-1) :
            if abs(arr[i][0]-arr[i+1][0]) > eps2 :
                return False
        return True

    def getRGB(self,px,py) :
        sz = self.sz // 2
        if px < sz-1 or py < sz-1 or px > self.width-1-sz or py > self.height-1-sz :
            summa = 0
            div = 0
            for i in range(-sz,sz+1) :
                for j in range(-sz,sz+1) :
                    if i < 0 or j < 0 or i >= self.width or j >= self.height :
                        continue
                    summa += tych(self.pix[i,j])
                    div += 3
            return summa / div
        return self.dp[px-sz][py-sz] / (self.sz * self.sz * 3)

    def makeRGB(self) :
        sz = 5
        self.sz = sz
        pix = self.im.load()
        self.pix = pix
        self.dp = [[256] * self.height for i in range(0,self.width)]
        self.dp[sz-1][sz-1] = 0
        for i in range(0,sz) :
            for j in range(0,sz) :
                self.dp[sz-1][sz-1] += tych(pix[i,j])
        for i in range(sz,self.width) :
            self.dp[i][sz-1] = self.dp[i-1][sz-1]
            for j in range(0,sz) :
                self.dp[i][sz-1] += tych(pix[i,j]) - tych(pix[i-sz,j])
        for i in range(sz,self.height) :
            self.dp[sz-1][i] = self.dp[sz-1][i-1]
            for j in range(0,sz) :
                self.dp[sz-1][i] += tych(pix[j,i]) - tych(pix[j,i-sz])
        for i in range(sz,self.width) :
            for j in range(sz,self.height) :
                self.dp[i][j] = self.dp[i-1][j] + self.dp[i][j-1] - self.dp[i-1][j-1]
                self.dp[i][j] += tych(pix[i,j]) + tych(pix[i-sz,j-sz]) - tych(pix[i,j-sz]) - tych(pix[i-sz,j])
        return

    def workingtest(self) :
        for i in range(0,self.width) :
            for j in range(0,self.height) :
                self.im.putpixel((i,j),(0,0,0))
        for j in self.listofpoint :
            for i in j:
                for a1 in range((int)(i[0]-3+self.width//2),(int)(i[0]+3+self.width//2)) :
                    for a2 in range((int)(i[1]-3+self.height//2),(int)(i[1]+3+self.height//2)) :
                        try :
                            self.im.putpixel((a1,a2),(255,255,255))
                        except :
                            pass
        self.im.save("test.png")

        
        
class W :
    def __init__(self) :
        self.w = tk.Tk()
        self.w.title("Messenger : Our connection to visually impaired")
        self.w.minsize(height = 100, width = 100)
        tk.Label(self.w, text = "File path:").grid(row=0, sticky = tk.W)
        self.entry = tk.Entry(self.w)
        self.entry.grid(row=0, column=1)
        self.button = tk.Button(self.w, text = "Translate", command = self.makeocr)
        self.button.grid(row=1, column=1)
        self.output = tk.Text(self.w, width = 50)
        self.output.grid(row=2, column=1)

    def makeocr(self) :
        getText = self.entry.get()
        ocr = Messenger(getText)
        if ocr.im == False :
            outputstring = "Such file dosen't exist.\nPlease check the name again."
        else :
            outputstring = ocr.start()
        self.output.delete('1.0', tk.END)
        self.output.insert('1.0',outputstring)

if __name__ == "__main__" :
    startpanel = W()
    
