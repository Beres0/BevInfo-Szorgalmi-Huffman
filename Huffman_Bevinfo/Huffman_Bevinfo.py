import os
import math

adat_elvalaszto=bytes("\00\50\00","ascii")
tartalom_elvalaszto=bytes("\00\00\100\00\00","ascii")
par_elvalaszto=bytes("\100\00\100","ascii")

def Szam_to_Bytes(szam:int)->bytes:
    bit_hossz=szam.bit_length()
    byte_hossz=bit_hossz>>3
    visszatolt=byte_hossz<<3
    byte_hossz=byte_hossz if bit_hossz==visszatolt else byte_hossz+1
    return szam.to_bytes(byte_hossz,"big")


class csomopont:

    def __init__(self):
        self.__szulo=None 

    @property
    def Szulo(self):
        return self.__szulo
    @property
    def Kod(self)->str:
        if(not self.GyokerE):
            if(self.Szulo.Jobb==self): return self.Szulo.Kod+"1"
            else:return self.Szulo.Kod+"0"
        else: return ""
    @property
    def Karakter(self)->str:
        pass
    @property
    def Gyakorisag(self)->int:
        pass
    @property
    def GyokerE(self)->bool:
        return self.Szulo is None
    def __repr__(self):
        return "("+self.Karakter+","+str(self.Gyakorisag)+","+self.Kod+")"


class csomopont_level(csomopont):
    def __init__(self,karakter:str,gyakorisag:int):
        super().__init__()
        self.__karakter=karakter
        self.__gyakorisag=gyakorisag
        
    @property
    def Bytes(self)->bytes:
        byte_array=bytearray()
        karakter=self.Karakter
        byte_array+=bytes(self.Karakter,"utf8")
        byte_array+=adat_elvalaszto
        byte_array+=Szam_to_Bytes(self.Gyakorisag)
        return bytes(byte_array)

    @property
    def Karakter(self)->str:
       return self.__karakter
    @property
    def Gyakorisag(self)->int:
       return self.__gyakorisag

class csomopont_szulo(csomopont):
    def __init__(self,bal:csomopont,jobb:csomopont):
        super().__init__()
        self.__bal=bal
        bal._csomopont__szulo=self
        self.__jobb=jobb;
        jobb._csomopont__szulo=self

    @property
    def Karakter(self)->str:
        return self.Bal.Karakter+self.Jobb.Karakter
    @property
    def Gyakorisag(self)->int:
        return self.Bal.Gyakorisag+self.Jobb.Gyakorisag
    @property
    def Bal(self)->csomopont:
        return self.__bal
    @property
    def Jobb(self)->csomopont:
        return self.__jobb

class Huffman_Fa:
   
    def Tisztit(self):
        self.__szoveg=None
        self.__levelek=None
        self.__gyoker=None
        self.__kodolt_szoveg_bin=None


    def Beolvas_Szovegfajlbol(self,utvonal:str):
        file=open(utvonal,"tr",encoding="utf8")
        szoveg=file.read()
        file.close
        self.Beolvas_Szoveg(szoveg)
    
    def Beolvas_Szoveg(self,szoveg:str):
        self.Tisztit()

        self.__szoveg=szoveg
        self.__keszit_levelek(self.__megszamol_gyakorisagok())
        self.__epit_fa()

    def __megszamol_gyakorisagok(self)->dict:
        gyakorisagok={}
        for k in self.__szoveg:
            if(k not in gyakorisagok): gyakorisagok[k]=0
            gyakorisagok[k]+=1
        return gyakorisagok

    def __keszit_levelek(self,gyakorisagok:dict):
        levelek_lista=[]
        for karakter in gyakorisagok:
            levelek_lista.append(csomopont_level(karakter,gyakorisagok[karakter]))
        levelek_lista.sort(key=lambda n: (n.Gyakorisag),reverse=True)
        self.__levelek=tuple(levelek_lista)

    def __epit_fa(self):
          csomopontok=list(self.Levelek)

          while(len(csomopontok)>1):
                utolso=csomopontok.pop()
                utolso_elotti=csomopontok.pop()
                szulo=csomopont_szulo(utolso,utolso_elotti)

                self.__beszur_szulo(csomopontok,szulo)
          self.__gyoker=csomopontok[0]


    def __beszur_szulo(self,csomopontok:list,szulo:csomopont_szulo):
        i=len(csomopontok)-1
        while(i>=0 and szulo.Gyakorisag>csomopontok[i].Gyakorisag):
            i-=1
        csomopontok.insert(i+1,szulo)

    def Dekodol_Fajlbol(self,utvonal):
        self.Tisztit()
        file=open(utvonal,"rb")
        kodolt=file.read()
        reszek=kodolt.partition(tartalom_elvalaszto)
        
        elso_sor=bytearray(reszek[0]).split(par_elvalaszto)
        gyakorisagok=self.__beolvas__gyakorisagok(elso_sor)
        self.__keszit_levelek(gyakorisagok)
        self.__epit_fa()

        kodol_bin=""
        bytes=bytearray(reszek[2])
        for b in bytes:
            kodol_bin+=format(b,"08b")

        utolso_byte=elso_sor[0].split(adat_elvalaszto)
        hossz=str(utolso_byte[0],"ascii")
        ertek=int(str(utolso_byte[1],"ascii"))

        if(hossz!="0"):
            kodol_bin+=format(ertek,"0"+hossz+"b")

        self.__kodolt_szoveg_bin=kodol_bin
            
    def __beolvas__gyakorisagok(self,elso_sor:bytearray)->dict:
        gyakorisagok={}
        for i in range(1,len(elso_sor)):
            elso_sor_split=elso_sor[i].split(adat_elvalaszto)
            kar_es_gyak=elso_sor[i].split(adat_elvalaszto)
            gyakorisagok[str(kar_es_gyak[0],"utf8")]=int.from_bytes(kar_es_gyak[1],byteorder="big")
        return gyakorisagok

    @property
    def Levelek(self)->tuple:
        return self.__levelek

    @property
    def Gyoker(self)->csomopont_szulo:
        return self.__gyoker

  
   
    @property
    def Szoveg(self)->str:
        self.__gyoker
        if(self.__szoveg is None):
            bin=self.Kodolt_Szoveg_Bin
            szotar=self.__keszit_forditott_szotar()
            szoveg=""
            kod=""
            for bit in bin:
                  kod+=bit
                  if(kod in szotar):
                      szoveg+=szotar[kod]
                      kod=""
            self.__szoveg=szoveg

        return self.__szoveg

    @property
    def Kodolt_Szoveg_Bin(self)->str:
        if(self.__kodolt_szoveg_bin is None):
               kodolt_lista=[]
               szotar=self.__keszit_szotar()

               for karakter in self.__szoveg:
                   kodolt_lista.append(szotar[karakter])
               self.__kodolt_szoveg_bin="".join(kodolt_lista)

        return self.__kodolt_szoveg_bin

    def __keszit_szotar(self)->dict:
        szotar={}
        for level in self.Levelek:
            szotar[level.Karakter]=level.Kod
        return szotar

    def __keszit_forditott_szotar(self)->dict:
        szotar={}
        for level in self.Levelek:
            szotar[level.Kod]=level.Karakter
        return szotar

    @property
    def Entropia(self):
        Hs=0
        szoveg_hossz=len(self.Szoveg)
        for level in self.Levelek:
            valoszinuseg=level.Gyakorisag/szoveg_hossz
            Hs+=valoszinuseg*math.log2(valoszinuseg)
            
        return -Hs

    @property
    def Max_Entropia(self):
        karakter_db=len(self.Levelek)
        return math.log2(karakter_db)

    @property
    def Redudancia(self):
        return 1-self.Entropia/self.Max_Entropia;

    @property
    def Atlagos_Kodhossz(self):
        atlag=0
        szoveg_hossz=len(self.Szoveg)
        for level in self.Levelek:
            atlag+=len(level.Kod)*level.Gyakorisag
        return atlag/szoveg_hossz

    def Szoveget_Ir_Fajlba(self,utvonal:str):
        file=open(utvonal,"w",encoding="utf8")
        file.write(self.Szoveg)
        file.close

    def Kodol_Fajlba(self,utvonal:str):
        file=open(utvonal,"bw")

        tartalom=bytearray()
        kodolt_szoveg=self.__kodol_szoveg()
        utolso_byte=kodolt_szoveg[1]

        tartalom+=bytes(utolso_byte[0],"ascii")
        tartalom+=adat_elvalaszto
        tartalom+=bytes(utolso_byte[1],"ascii")
        tartalom+=par_elvalaszto
        tartalom+=self.__kodol_szotar()
        tartalom+=tartalom_elvalaszto
        tartalom+=kodolt_szoveg[0]

        file.write(tartalom)
        file.close

    def __kodol_szoveg(self)->tuple:
        kodolt_bin=self.Kodolt_Szoveg_Bin
        kodolt_bin_hossz=len(kodolt_bin)
        utolso_byte_hossz=kodolt_bin_hossz%8
        utolso_byte_kezdete=kodolt_bin_hossz-utolso_byte_hossz
        
        utolso_byte_ertek=0
        if(utolso_byte_hossz>0):
            utolso_byte_ertek=int(kodolt_bin[utolso_byte_kezdete:kodolt_bin_hossz],base=2)
        
        utolso_byte=(str(utolso_byte_hossz),str(utolso_byte_ertek))

        kodolt_szoveg_bytes=bytearray()
        i=0
        while(i<utolso_byte_kezdete):
            bin_test=kodolt_bin[i:i+8]
            kodolt_szoveg_bytes.append(int(kodolt_bin[i:i+8],base=2))
            i+=8

        return (kodolt_szoveg_bytes,utolso_byte)

    def __kodol_szotar(self)->bytearray:
        szotar=bytearray()
        
        szotar+=self.Levelek[0].Bytes

        for i in range(1,len(self.Levelek)):
            szotar+=par_elvalaszto
            szotar+=self.Levelek[i].Bytes
        return szotar













  
