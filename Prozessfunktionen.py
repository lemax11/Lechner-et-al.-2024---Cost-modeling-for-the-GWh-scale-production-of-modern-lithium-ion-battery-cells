# -*- coding: utf-8 -*-iebs
"""
Created on Wed Feb 24 10:08:39 2021

@1st author: bendzuck
@2nd author: mahin
"""
import pandas as pd
import json
import math
import copy

#____________________________________
  

class basis_prozessschritt:
    def __init__(self,df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary):
        if "Operating days" in schritt_dictionary:
           self.arbeitstage_pro_jahr = schritt_dictionary["Operating days"]
        else:
            self.arbeitstage_pro_jahr = 360

        if "Space" in schritt_dictionary:
           self.anteil_anlagengrundflaeche = schritt_dictionary["Space"]
        else:
            self.anteil_anlagengrundflaeche = 0
        self.df = df
        self.Zellergebnisse = Zellergebnisse
        self.Zellchemie = Zellchemie
        self.Materialinfos = Materialinfos
            
    def variabler_aussschuss(self,dictionary):
        dictionary["Cell equivalent"]        = dictionary["Cell equivalent"]/(1-self.df["Wert"]["Variable scrap rate"]/100) #[-]
        dictionary["Anode collector"]       = dictionary["Anode collector"]/(1-self.df["Wert"]["Variable scrap rate"]/100) #[m]
        dictionary["Cathode collector"]     = dictionary["Cathode collector"]/(1-self.df["Wert"]["Variable scrap rate"]/100) #[m]
        dictionary["Anode coating"]    = dictionary["Anode coating"]/(1-self.df["Wert"]["Variable scrap rate"]/100) #[kg]
        dictionary["Cathode coating"]  = dictionary["Cathode coating"]/(1-self.df["Wert"]["Variable scrap rate"]/100) #[kg]
        dictionary["Separator"]             = dictionary["Separator"]/(1-self.df["Wert"]["Variable scrap rate"]/100) #[m]
        dictionary["Case"]                 = dictionary["Case"]/(1-self.df["Wert"]["Variable scrap rate"]/100) #[l]
        dictionary["Electrolyte"]            = dictionary["Electrolyte"]/(1-self.df["Wert"]["Variable scrap rate"]/100) #[l]
        
        return dictionary

    def mitarbeiter_anlagen(self,dictionary):
        dictionary["Skilled workers"]   =   (self.Anlagen_Anode+self.Anlagen_Kathode)*self.df["Wert"]["Specialists"] #[-]
        dictionary["Assistants"]     =   (self.Anlagen_Anode+self.Anlagen_Kathode)*self.df["Wert"]["Support staff"] #[-]
        
        return dictionary
    
    def mitarbeiter_schicht(self,dictionary):
        dictionary["Skilled workers"]   =   self.df["Wert"]["Personal Facharbeiter"] #[-]
        dictionary["Assistants"]     =   self.df["Wert"]["Personal Hilfskräfte"] #[-]
        
        return dictionary
        
    def flaechen(self,dictionary):
        dictionary["Space requirements normal room"]             =   (self.Anlagen_Anode+self.Anlagen_Kathode)*self.df["Wert"]["Required space regular conditions"]/ self.anteil_anlagengrundflaeche
 #[m²]
        dictionary["Space requirements for dry room"] =   (self.Anlagen_Anode+self.Anlagen_Kathode)*self.df["Wert"]["Required space dry room"]/ self.anteil_anlagengrundflaeche#[m²]
        
        return dictionary
            
    def energie(self,dictionary):
        dictionary["Energy demand"] =   (self.Anlagen_Anode*self.df["Wert"]["Power consumption anode"]+\
                                        self.Anlagen_Kathode*self.df["Wert"]["Power consumption cathode"])*24*self.arbeitstage_pro_jahr #[kWh]
        return dictionary
    
    def investition(self,dictionary):
        dictionary["Investment"] = self.Anlagen_Anode*self.df["Wert"]["Investment anode"] + self.Anlagen_Kathode*self.df["Wert"]["Investment cathode"] #[€]
        return dictionary

    def ueberkapazitaet(self, dictionary):
        faktor_ueberkapazitaet = 1 + self.df["Wert"]["Excess capacity"]/100
        self.Anlagen_Anode = math.ceil(self.Anlagen_Anode*faktor_ueberkapazitaet)
        self.Anlagen_Kathode = math.ceil(self.Anlagen_Kathode*faktor_ueberkapazitaet)
        return dictionary
    
    def neue_materialien(self,dictionary,neue_materialien=""):
        neue_materialen_liste = dictionary["Neue Materialien"].split(';')
        if neue_materialen_liste != [""]:
            for material in neue_materialen_liste:
                dictionary[material]=0
                dictionary[material+" recovery"]=0
            dictionary["Neue Materialien"] = neue_materialien
            return dictionary
        else:
            dictionary["Neue Materialien"] = neue_materialien
            return dictionary
#____________________________________
#Prozessschritte für Suspensionen
class suspension_prozessschritt(basis_prozessschritt):
    def rueckgewinnung(self,dictionary,rueckgewinnung):
        dictionary["Anode collector recovery"]       = dictionary["Anode collector"]*(self.df["Wert"]["Variable scrap rate"]/100) #[m]
        dictionary["Cathode collector recovery"]     = dictionary["Cathode collector"]*(self.df["Wert"]["Variable scrap rate"]/100) #[m]
        dictionary["Anode coating recovery"]    = dictionary["Anode coating"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Slurry raw materials anode"]/100 #[kg]
        dictionary["Cathode coating recovery"]  = dictionary["Cathode coating"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Slurry raw materials cathode"]/100 #[kg]
        dictionary["Separator recovery"]             = dictionary["Separator"]*(self.df["Wert"]["Variable scrap rate"]/100) #[m]
        dictionary["Case recovery"]                 = dictionary["Case"]*(self.df["Wert"]["Variable scrap rate"]/100) #[l]
        dictionary["Electrolyte recovery"]            = dictionary["Electrolyte"]*(self.df["Wert"]["Variable scrap rate"]/100) #[l]
        
        return dictionary

    def fixausschuss(self,dictionary,rueckgewinnung):

        return dictionary

#____________________________________
#Prozessschritte für Rolle-zu-Rolle Prozesse
class coil_prozessschritt(basis_prozessschritt):
    def rueckgewinnung(self,dictionary,rueckgewinnung):
        dictionary["Anode collector recovery"]       = dictionary["Anode collector"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Anode"]/100 #[m]
        dictionary["Cathode collector recovery"]     = dictionary["Cathode collector"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Cathode"]/100 #[m]
        dictionary["Anode coating recovery"]    = dictionary["Anode coating"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Anode"]/100 #[kg]
        dictionary["Cathode coating recovery"]  = dictionary["Cathode coating"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Cathode"]/100 #[kg]
        dictionary["Separator recovery"]             = dictionary["Separator"]*(self.df["Wert"]["Variable scrap rate"]/100) #[m]
        dictionary["Case recovery"]                 = dictionary["Case"]*(self.df["Wert"]["Variable scrap rate"]/100) #[l]
        dictionary["Electrolyte recovery"]            = dictionary["Electrolyte"]*(self.df["Wert"]["Variable scrap rate"]/100) #[l]
        
        return dictionary

    def anlagen_coating_drying(self,dictionary):
        Zellen_pro_Tag = dictionary["Cell equivalent"]/self.arbeitstage_pro_jahr

        Meter_Anode_pro_Tag = Zellen_pro_Tag*self.Zellergebnisse["Wert"]["Number of repeating units"]/self.Zellergebnisse["Wert"]["Sheets/meter anode"] #[m]
        Meter_Kathode_pro_Tag = Zellen_pro_Tag*self.Zellergebnisse["Wert"]["Number of repeating units"]/self.Zellergebnisse["Wert"]["Sheets/meter cathode"] #[m]

        Meter_Anode_pro_Minute = Meter_Anode_pro_Tag/(24*60)
        Meter_Kathode_pro_Minute = Meter_Kathode_pro_Tag/(24*60)
        
        Anodenkollektorfolie = self.Zellchemie.loc[self.Zellchemie['Kategorie'] == "Collector foil anode"].index.tolist()[0]
        meter_anodenkollektorfolie_pro_rolle = read_zellinfo(Anodenkollektorfolie,self.Materialinfos)["Wert"]["Coil length"]
        Kathodenkollektorfolie = self.Zellchemie.loc[self.Zellchemie['Kategorie'] == "Collector foil cathode"].index.tolist()[0]
        meter_kathodenkollektorfolie_pro_rolle = read_zellinfo(Kathodenkollektorfolie,self.Materialinfos)["Wert"]["Coil length"]
        
        Zeit_pro_Coil_Anode = meter_anodenkollektorfolie_pro_rolle/float(self.df["Wert"]["Coating speed anode"]) #[min]
        Verlust_durch_Nebenzeit_Anode = self.df["Wert"]["Auxiliary process time anode"]/Zeit_pro_Coil_Anode #[%]
        
        Zeit_pro_Coil_Kathode = meter_kathodenkollektorfolie_pro_rolle/float(self.df["Wert"]["Coating speed cathode"])
        Verlust_durch_Nebenzeit_Kathode = float(self.df["Wert"]["Auxiliary process time cathode"])/Zeit_pro_Coil_Kathode #[%]
        
        Anlagen_Anode = math.ceil(Meter_Anode_pro_Minute/float(self.df["Wert"]["Coating speed anode"])*(1+Verlust_durch_Nebenzeit_Anode))
        Anlagen_Kathode = math.ceil(Meter_Kathode_pro_Minute/float(self.df["Wert"]["Coating speed cathode"])*(1+Verlust_durch_Nebenzeit_Kathode))

        Anz_Maschinen = "{} Anode, {} Cathode".format(Anlagen_Anode,Anlagen_Kathode)

        self.Anlagen_Anode = Anlagen_Anode
        self.Anlagen_Kathode = Anlagen_Kathode

        dictionary["Number of machines"] = Anz_Maschinen

        return dictionary
    
    def anlagen_calendering(self,dictionary):
        Zellen_pro_Tag = dictionary["Cell equivalent"]/self.arbeitstage_pro_jahr

        Meter_Anode_pro_Tag = Zellen_pro_Tag*self.Zellergebnisse["Wert"]["Number of repeating units"]/self.Zellergebnisse["Wert"]["Sheets/meter anode"] #[m]
        Meter_Kathode_pro_Tag = Zellen_pro_Tag*self.Zellergebnisse["Wert"]["Number of repeating units"]/self.Zellergebnisse["Wert"]["Sheets/meter cathode"] #[m]

        Meter_Anode_pro_Minute = Meter_Anode_pro_Tag/(24*60)
        Meter_Kathode_pro_Minute = Meter_Kathode_pro_Tag/(24*60)
        
        Anodenkollektorfolie = self.Zellchemie.loc[self.Zellchemie['Kategorie'] == "Collector foil anode"].index.tolist()[0]
        meter_anodenkollektorfolie_pro_rolle = read_zellinfo(Anodenkollektorfolie,self.Materialinfos)["Wert"]["Coil length"]
        Kathodenkollektorfolie = self.Zellchemie.loc[self.Zellchemie['Kategorie'] == "Collector foil cathode"].index.tolist()[0]
        meter_kathodenkollektorfolie_pro_rolle = read_zellinfo(Kathodenkollektorfolie,self.Materialinfos)["Wert"]["Coil length"]
        
        Zeit_pro_Coil_Anode = meter_anodenkollektorfolie_pro_rolle/float(self.df["Wert"]["Calendering speed anode"]) #[min]
        Verlust_durch_Nebenzeit_Anode = self.df["Wert"]["Auxiliary process time anode"]/Zeit_pro_Coil_Anode #[%]
        
        Zeit_pro_Coil_Kathode = meter_kathodenkollektorfolie_pro_rolle/float(self.df["Wert"]["Calendering speed cathode"])
        Verlust_durch_Nebenzeit_Kathode = float(self.df["Wert"]["Auxiliary process time cathode"])/Zeit_pro_Coil_Kathode #[%]
        
        Anlagen_Anode = math.ceil(Meter_Anode_pro_Minute/float(self.df["Wert"]["Calendering speed anode"])*(1+Verlust_durch_Nebenzeit_Anode))
        Anlagen_Kathode = math.ceil(Meter_Kathode_pro_Minute/float(self.df["Wert"]["Calendering speed cathode"])*(1+Verlust_durch_Nebenzeit_Kathode))

        Anz_Maschinen = "{} Anode, {} Cathode".format(Anlagen_Anode,Anlagen_Kathode)

        self.Anlagen_Anode = Anlagen_Anode
        self.Anlagen_Kathode = Anlagen_Kathode

        dictionary["Number of machines"] = Anz_Maschinen

        return dictionary
    def anlagen_slitting(self,dictionary):
        Zellen_pro_Tag = dictionary["Cell equivalent"]/self.arbeitstage_pro_jahr

        Meter_Anode_pro_Tag = Zellen_pro_Tag*self.Zellergebnisse["Wert"]["Number of repeating units"]/self.Zellergebnisse["Wert"]["Sheets/meter anode"] #[m]
        Meter_Kathode_pro_Tag = Zellen_pro_Tag*self.Zellergebnisse["Wert"]["Number of repeating units"]/self.Zellergebnisse["Wert"]["Sheets/meter cathode"] #[m]

        Meter_Anode_pro_Minute = Meter_Anode_pro_Tag/(24*60)
        Meter_Kathode_pro_Minute = Meter_Kathode_pro_Tag/(24*60)
        
        Anodenkollektorfolie = self.Zellchemie.loc[self.Zellchemie['Kategorie'] == "Collector foil anode"].index.tolist()[0]
        meter_anodenkollektorfolie_pro_rolle = read_zellinfo(Anodenkollektorfolie,self.Materialinfos)["Wert"]["Coil length"]
        Kathodenkollektorfolie = self.Zellchemie.loc[self.Zellchemie['Kategorie'] == "Collector foil cathode"].index.tolist()[0]
        meter_kathodenkollektorfolie_pro_rolle = read_zellinfo(Kathodenkollektorfolie,self.Materialinfos)["Wert"]["Coil length"]
        
        Zeit_pro_Coil_Anode = meter_anodenkollektorfolie_pro_rolle/float(self.df["Wert"]["Slitting speed anode"]) #[min]
        Verlust_durch_Nebenzeit_Anode = self.df["Wert"]["Auxiliary process time anode"]/Zeit_pro_Coil_Anode #[%]
        
        Zeit_pro_Coil_Kathode = meter_kathodenkollektorfolie_pro_rolle/float(self.df["Wert"]["Slitting speed cathode"])
        Verlust_durch_Nebenzeit_Kathode = float(self.df["Wert"]["Auxiliary process time cathode"])/Zeit_pro_Coil_Kathode #[%]
        
        Anlagen_Anode = math.ceil(Meter_Anode_pro_Minute/float(self.df["Wert"]["Slitting speed anode"])*(1+Verlust_durch_Nebenzeit_Anode))
        Anlagen_Kathode = math.ceil(Meter_Kathode_pro_Minute/float(self.df["Wert"]["Slitting speed cathode"])*(1+Verlust_durch_Nebenzeit_Kathode))

        Anz_Maschinen = "{} Anode, {} Cathode".format(Anlagen_Anode,Anlagen_Kathode)

        self.Anlagen_Anode = Anlagen_Anode
        self.Anlagen_Kathode = Anlagen_Kathode

        dictionary["Number of machines"] = Anz_Maschinen

        return dictionary

    def flaechen_getrennt(self,dictionary):
        dictionary["Space requirements normal room"]             =   (self.Anlagen_Anode*self.df["Wert"]["Required space regular environment anode"]+\
                                                    self.Anlagen_Kathode*self.df["Wert"]["Required space regular environment cathode"])/self.anteil_anlagengrundflaeche#[m²]

        dictionary["Space requirements for dry room"] =   (self.Anlagen_Anode*self.df["Wert"]["Required space dry room anode"]+\
                                                    self.Anlagen_Kathode*self.df["Wert"]["Required space dry room cathode"])/self.anteil_anlagengrundflaeche #[m²]
        return dictionary

    #Fixausschuss pro Coil
    def fixausschuss(self,dictionary,rueckgewinnung):       
        Anodenkollektorfolie = self.Zellchemie.loc[self.Zellchemie['Kategorie'] == "Collector foil anode"].index.tolist()[0]
        meter_anodenkollektorfolie_pro_rolle = read_zellinfo(Anodenkollektorfolie,self.Materialinfos)["Wert"]["Coil length"]
        Kathodenkollektorfolie = self.Zellchemie.loc[self.Zellchemie['Kategorie'] == "Collector foil cathode"].index.tolist()[0]
        meter_kathodenkollektorfolie_pro_rolle = read_zellinfo(Kathodenkollektorfolie,self.Materialinfos)["Wert"]["Coil length"]
        
        Zusatzverlust_Anode = self.df["Wert"]["Fixed scrap rate"]/meter_anodenkollektorfolie_pro_rolle
        Zusatzverlust_Kathode = self.df["Wert"]["Fixed scrap rate"]/meter_kathodenkollektorfolie_pro_rolle
        
        Zusatzverlust = (Zusatzverlust_Anode+Zusatzverlust_Kathode)/2
        
        dictionary["Cell equivalent"]        = dictionary["Cell equivalent"]/(1-Zusatzverlust)
        dictionary["Anode collector"]       = dictionary["Anode collector"]/(1-Zusatzverlust)
        dictionary["Cathode collector"]     = dictionary["Cathode collector"]/(1-Zusatzverlust)
        dictionary["Anode coating"]    = dictionary["Anode coating"]/(1-Zusatzverlust)
        dictionary["Cathode coating"]  = dictionary["Cathode coating"]/(1-Zusatzverlust)
        dictionary["Separator"]             = dictionary["Separator"]/(1-Zusatzverlust)
        dictionary["Case"]                 = dictionary["Case"]/(1-Zusatzverlust)
        dictionary["Electrolyte"]            = dictionary["Electrolyte"]/(1-Zusatzverlust)

        dictionary["Anode collector recovery"] = dictionary["Anode collector recovery"]+dictionary["Anode collector"]*Zusatzverlust_Anode*rueckgewinnung["Wert"]["Anode collector"]/100
        dictionary["Cathode collector recovery"] = dictionary["Cathode collector recovery"]+dictionary["Cathode collector"]*Zusatzverlust_Kathode*rueckgewinnung["Wert"]["Cathode collector"]/100
        
        return dictionary
    
#____________________________________
#Prozessschritte für Elektrodenblätter     
class sheet_prozessschritt(basis_prozessschritt):
    def rueckgewinnung(self,dictionary,rueckgewinnung):
        dictionary["Anode collector recovery"]       = dictionary["Anode collector"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Anode"]/100 #[m]
        dictionary["Cathode collector recovery"]     = dictionary["Cathode collector"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Cathode"]/100 #[m]
        dictionary["Anode coating recovery"]    = dictionary["Anode coating"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Anode"]/100 #[kg]
        dictionary["Cathode coating recovery"]  = dictionary["Cathode coating"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Cathode"]/100 #[kg]
        dictionary["Separator recovery"]             = dictionary["Separator"]*(self.df["Wert"]["Variable scrap rate"]/100) #[m]
        dictionary["Case recovery"]                 = dictionary["Case"]*(self.df["Wert"]["Variable scrap rate"]/100) #[l]
        dictionary["Electrolyte recovery"]            = dictionary["Electrolyte"]*(self.df["Wert"]["Variable scrap rate"]/100) #[l]
        
        return dictionary

    def fixausschuss(self,dictionary,rueckgewinnung):
        WHE_pro_tag = dictionary["Cell equivalent"]/self.arbeitstage_pro_jahr*(self.Zellergebnisse["Wert"]['Number of repeating units'])
        sheet_pro_tag = WHE_pro_tag*2
        Fixausschuss = self.df["Wert"]["Fixed scrap rate"]#Stk./d
        
        Zusatzverlust = Fixausschuss/sheet_pro_tag      
        
        dictionary["Cell equivalent"]        = dictionary["Cell equivalent"]/(1-Zusatzverlust)
        dictionary["Anode collector"]       = dictionary["Anode collector"]/(1-Zusatzverlust)
        dictionary["Cathode collector"]     = dictionary["Cathode collector"]/(1-Zusatzverlust)
        dictionary["Anode coating"]    = dictionary["Anode coating"]/(1-Zusatzverlust)
        dictionary["Cathode coating"]  = dictionary["Cathode coating"]/(1-Zusatzverlust)
        dictionary["Separator"]             = dictionary["Separator"]/(1-Zusatzverlust)
        dictionary["Electrolyte"]            = dictionary["Electrolyte"]/(1-Zusatzverlust)

        dictionary["Anode collector recovery"] = dictionary["Anode collector recovery"]+dictionary["Anode collector"]*Zusatzverlust*rueckgewinnung["Wert"]["Anode collector"]/100
        dictionary["Cathode collector recovery"] = dictionary["Cathode collector recovery"]+dictionary["Cathode collector"]*Zusatzverlust*rueckgewinnung["Wert"]["Cathode collector"]/100
        dictionary["Anode coating recovery"] = dictionary["Anode coating recovery"]+dictionary["Anode coating"]*Zusatzverlust*rueckgewinnung["Wert"]["Anode coating"]/100
        dictionary["Cathode coating recovery"] = dictionary["Cathode coating recovery"]+dictionary["Cathode coating"]*Zusatzverlust*rueckgewinnung["Wert"]["Cathode coating"]/100

        return dictionary
    
    def anlagen(self,dictionary):
        Zellen_pro_Tag = dictionary["Cell equivalent"]/self.arbeitstage_pro_jahr
        Zeit_pro_Zelle = (self.Zellergebnisse["Wert"]['Number of repeating units']*4)/float(self.df["Wert"]["Geschwindigkeit"])+float(self.df["Wert"]["Nebenzeiten"]) #[s]
        Anz_Maschinen = math.ceil(Zellen_pro_Tag/(24*60*60/Zeit_pro_Zelle))
        dictionary["Number of machines"] = Anz_Maschinen
        self.Anlagen = Anz_Maschinen
        
        return dictionary

    def ueberkapazitaet(self, dictionary):
        faktor_ueberkapazitaet = 1 + self.df["Wert"]["Excess capacity"]/100
        self.Anlagen = math.ceil(self.Anlagen*faktor_ueberkapazitaet)
        return dictionary
    
    def mitarbeiter_anlagen(self,dictionary):
        dictionary["Skilled workers"]   =   (self.Anlagen)*self.df["Wert"]["Specialists"]
        dictionary["Assistants"]     =   (self.Anlagen)*self.df["Wert"]["Support staff"]
        
        return dictionary
    
    def energie(self,dictionary):
        dictionary["Energy demand"] =   (self.Anlagen)*self.df["Wert"]["Power consumption"]*24*self.arbeitstage_pro_jahr
        
        return dictionary
    
    def investition(self,dictionary):
        dictionary["Investment"] = self.Anlagen*self.df["Wert"]["Investment"]
        
        return dictionary
    
    def flaechen(self,dictionary):
        dictionary["Space requirements normal room"]             =   (self.Anlagen)*self.df["Wert"]["Required space regular conditions"]/self.anteil_anlagengrundflaeche
        dictionary["Space requirements for dry room"] =   (self.Anlagen)*self.df["Wert"]["Required space dry room"]/self.anteil_anlagengrundflaeche
 
        return dictionary

#____________________________________
#Prozessschritte für Zellen         
class zelle_prozessschritt(basis_prozessschritt):
    def rueckgewinnung(self,dictionary,rueckgewinnung):
        dictionary["Anode collector recovery"]       = dictionary["Anode collector"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Filled cell"]/100 #[m]
        dictionary["Cathode collector recovery"]     = dictionary["Cathode collector"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Filled cell"]/100 #[m]
        dictionary["Anode coating recovery"]    = dictionary["Anode coating"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Filled cell"]/100 #[kg]
        dictionary["Cathode coating recovery"]  = dictionary["Cathode coating"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Filled cell"]/100 #[kg]
        dictionary["Separator recovery"]             = dictionary["Separator"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Filled cell"]/100 #[m]
        dictionary["Case recovery"]                 = dictionary["Case"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Filled cell"]/100 #[l]
        dictionary["Electrolyte recovery"]            = dictionary["Electrolyte"]*(self.df["Wert"]["Variable scrap rate"]/100)*rueckgewinnung["Wert"]["Filled cell"]/100 #[l]
        
        return dictionary

    def anlagen(self,dictionary):
        Zellen_pro_Tag = dictionary["Cell equivalent"]/self.arbeitstage_pro_jahr+self.df["Wert"]["Fixed scrap rate"]
        Zellen_pro_Minute = Zellen_pro_Tag/(24*60)
        Zellen_pro_Minute = 1/(1/Zellen_pro_Minute+self.df["Wert"]["Auxiliary process time"]) 
        Anz_Maschinen = math.ceil(Zellen_pro_Minute/float(self.df["Wert"]["Operating speed"]))
        dictionary["Number of machines"] = Anz_Maschinen
        self.Anlagen = Anz_Maschinen
        return dictionary
    
    def mitarbeiter_anlagen(self,dictionary):
        dictionary["Skilled workers"]   =   (self.Anlagen)*self.df["Wert"]["Specialists"]
        dictionary["Assistants"]     =   (self.Anlagen)*self.df["Wert"]["Support staff"]
        
        return dictionary
    
    def energie(self,dictionary):
        dictionary["Energy demand"] =   (self.Anlagen)*self.df["Wert"]["Power consumption"]*24*self.arbeitstage_pro_jahr
                
        return dictionary

    def ueberkapazitaet(self, dictionary):
        faktor_ueberkapazitaet = 1 + self.df["Wert"]["Excess capacity"]/100
        self.Anlagen = math.ceil(self.Anlagen*faktor_ueberkapazitaet)
        return dictionary
    
    def investition(self,dictionary):
        dictionary["Investment"] = self.Anlagen*self.df["Wert"]["Investment"]
        
        return dictionary
    
    def flaechen(self,dictionary):
        dictionary["Space requirements normal room"]             =   (self.Anlagen)*self.df["Wert"]["Required space regular conditions"]/self.anteil_anlagengrundflaeche
        dictionary["Space requirements for dry room"] =   (self.Anlagen)*self.df["Wert"]["Required space dry room"]/self.anteil_anlagengrundflaeche

        return dictionary
    
    def fixausschuss(self,dictionary,rueckgewinnung):
        
        return dictionary

#____________________________________
#Allgemeine Funktionen

# Wenn vom vorherigen Schritt "neu hinzugefügte Materialien" übergeben werden, werden diese in diesem Schritt auf 0 gesetzt
# Zunächst werden die übergebenen vom str mit ";" getrennt in liste umgewandelt 
def neue_materialien_zu_liste(neue_materialen):
    liste = neue_materialen.split(';')
    return liste
# hier wird die Liste der vormals neuen Materialien durchgegange und auf 0 gesetzt
def materialien_null_setzen(neue_materialen_liste,dictionary):
    if neue_materialen_liste == [""]:
        return dictionary
    else:
        for material in neue_materialen_liste:
            dictionary[material]=0
        return dictionary

def read_zellinfo(Material, df):
    df = df.loc[df["Material"] == Material]
    return df


#____________________________________
#Prozessfunktionen
#____________________________________________________________________________
#Prozesse fürs Paper

#PHEV 2 Produktion

def PHEV2_mixing(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = suspension_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
     
    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr

    Liter_Anode_pro_Tag = Zellen_pro_Tag*Zellergebnisse["Wert"]["Weight of the anode coating"]/Zellergebnisse["Wert"]["Density of the anode coating"]*(1/(Zellchemie["Wert"]["Solid content of anode"]/100))/1000 #[l]
    Liter_Kathode_pro_Tag = Zellen_pro_Tag*Zellergebnisse["Wert"]["Weight of the cathode coating"]/Zellergebnisse["Wert"]["Density of the cathode coating"]*(1/(Zellchemie["Wert"]["Solid content of cathode"]/100))/1000 #[l]

    Anlagen_Anode = math.ceil((Liter_Anode_pro_Tag/float(df["Wert"]["Usable volume of mixer anode"]))*float(df["Wert"]["Mixing time per batch anode"])/(24*60))
    Anlagen_Kathode = math.ceil((Liter_Kathode_pro_Tag/float(df["Wert"]["Usable volume of mixer cathode"]))*float(df["Wert"]["Mixing time per batch cathode"])/(24*60))
    
    process.Anlagen_Anode = Anlagen_Anode
    process.Anlagen_Kathode = Anlagen_Kathode

    schritt_dictionary["Energy demand"] = (Anlagen_Anode*float(df["Wert"]["Power consumption per mixer anode"])+Anlagen_Kathode*float(df["Wert"]["Power consumption per mixer cathode"]))*24*process.arbeitstage_pro_jahr
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)

    process.Anlagen_Anode = math.ceil(process.Anlagen_Anode*(1+df["Wert"]["Excess capacity"]/100))
    process.Anlagen_Kathode = math.ceil(process.Anlagen_Kathode*(1+df["Wert"]["Excess capacity"]/100))

    Anlagen_Dosierer_Anode = math.ceil(Anlagen_Anode/float(df["Wert"]["Number of mixers per dosing unit (anode)"]))
    Anlagen_Dosierer_Kathode = math.ceil(Anlagen_Kathode/float(df["Wert"]["Number of mixers per dosing unit(cathode)"]))

    schritt_dictionary["Number of machines"] = "{} Mixer Anode, {} -Cathode, {} Dispenser Anode, {} -Cathode".format(Anlagen_Anode,Anlagen_Kathode,Anlagen_Dosierer_Anode,Anlagen_Dosierer_Kathode)
    
    schritt_dictionary["Investment"] =   Anlagen_Anode *float(df["Wert"]["Investment cost anode"]) +\
                    Anlagen_Kathode *float(df["Wert"]["Investment cost cathode"])+\
                    Anlagen_Dosierer_Anode*float(df["Wert"]["Investment cost dosing unit (anode)"])+\
                    Anlagen_Dosierer_Kathode*float(df["Wert"]["Investment cost dosing unit (cathode)"])
                    
    schritt_dictionary["Space requirements normal room"] = (process.Anlagen_Anode*float(df["Wert"]["Required space regular environment mixer anode"]) +\
                                          process.Anlagen_Kathode*float(df["Wert"]["Required space regular environment mixer cathode"]) +\
                                         (Anlagen_Dosierer_Anode+Anlagen_Dosierer_Kathode)*float(df["Wert"]["Required space regular environment dosing unit"]))/process.anteil_anlagengrundflaeche

    schritt_dictionary["Space requirements for dry room"] = (process.Anlagen_Anode*float(df["Wert"]["Required space dry room mixer anode"]) +\
                                          process.Anlagen_Kathode*float(df["Wert"]["Required space dry room mixer cathode"]) +\
                                         (Anlagen_Dosierer_Anode+Anlagen_Dosierer_Kathode)*float(df["Wert"]["Required space dry room dosing unit"]))/process.anteil_anlagengrundflaeche

    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Anode coating;Cathode coating")
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary


def PHEV2_coating_and_drying(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.fixausschuss(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen_coating_drying(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)

    Drying_duration_anode = Zellergebnisse["Wert"]["Areal mass of anode coating"]*(1-(Zellchemie["Wert"]["Solid content of anode"]/100))/(Zellchemie["Wert"]["Solid content of anode"]/100)*(1/float(df["Wert"]["Drying rate"]))*10000/60/1000 #[min]
    print(Drying_duration_anode)
    Drying_duration_cathode = Zellergebnisse["Wert"]["Areal mass of cathode coating"]*(1-(Zellchemie["Wert"]["Solid content of cathode"]/100))/(Zellchemie["Wert"]["Solid content of cathode"]/100)*(1/float(df["Wert"]["Drying rate"]))*10000/60/1000 #[min]
    print(Drying_duration_cathode)

    Trocknerlänge_Anode = float(df["Wert"]["Coating speed anode"])*Drying_duration_anode #[m]
    Trocknerlänge_Kathode = float(df["Wert"]["Coating speed cathode"])*Drying_duration_cathode #[m]
    
    Anlagengrundfläche_Anode = df["Wert"]["Machine width"]*(df["Wert"]["Length of coating head"]+Trocknerlänge_Anode) #[m²]
    Anlagengrundfläche_Kathode = df["Wert"]["Machine width"]*(df["Wert"]["Length of coating head"]+Trocknerlänge_Kathode) #[m2]
    
    schritt_dictionary["Space requirements normal room"] = (Anlagengrundfläche_Anode*(1-float(df["Wert"]["Anode machines placed in dry room"]))*process.Anlagen_Anode+\
                                          Anlagengrundfläche_Kathode*(1-float(df["Wert"]["Cathode machines placed in dry room"]))*process.Anlagen_Kathode)/process.anteil_anlagengrundflaeche #[m²]

    schritt_dictionary["Space requirements for dry room"]  = (Anlagengrundfläche_Anode*(float(df["Wert"]["Anode machines placed in dry room"]))*process.Anlagen_Anode+\
                                          Anlagengrundfläche_Kathode*(float(df["Wert"]["Cathode machines placed in dry room"]))*process.Anlagen_Kathode)/process.anteil_anlagengrundflaeche #[m²]
    schritt_dictionary["Number of machines"] = process.Anlagen_Anode+process.Anlagen_Kathode
    schritt_dictionary = process.investition(schritt_dictionary)
    
    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Anode collector;Cathode collector")
    schritt_dictionary["Space requirement laboratory"] = 0

    return schritt_dictionary

def PHEV2_calendering(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen_calendering(schritt_dictionary)   
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen_getrennt(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def PHEV2_slitting(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.fixausschuss(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen_slitting(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen_getrennt(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def PHEV2_post_drying(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.fixausschuss(schritt_dictionary,rueckgewinnung)

    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr

    Anodenkollektorfolie = Zellchemie.loc[Zellchemie['Kategorie'] == "Collector foil anode"].index.tolist()[0]
    Kathodenkollektorfolie = Zellchemie.loc[Zellchemie['Kategorie'] == "Collector foil cathode"].index.tolist()[0]

    Meter_Anode_pro_Tag = Zellen_pro_Tag*Zellergebnisse["Wert"]["Number of repeating units"]/Zellergebnisse["Wert"]["Sheets/meter anode"] #[m]
    Meter_Kathode_pro_Tag = Zellen_pro_Tag*Zellergebnisse["Wert"]["Number of repeating units"]/Zellergebnisse["Wert"]["Sheets/meter cathode"] #[m]

    Meter_Anode_pro_Minute = Meter_Anode_pro_Tag/(24*60)
    Meter_Kathode_pro_Minute = Meter_Kathode_pro_Tag/(24*60)

    Geschwindigkeit_Anode = float(df["Wert"]["Throughput anode"])/(read_zellinfo(Anodenkollektorfolie,Materialinfos)["Wert"]["Width"]/1000)/(8*60)
    Geschwindigkeit_Kathode = float(df["Wert"]["Throughput cathode"])/(read_zellinfo(Kathodenkollektorfolie,Materialinfos)["Wert"]["Width"]/1000)/(8*60)
    
    meter_anodenkollektorfolie_pro_rolle = read_zellinfo(Anodenkollektorfolie,Materialinfos)["Wert"]["Coil length"]
    meter_kathodenkollektorfolie_pro_rolle = read_zellinfo(Kathodenkollektorfolie,Materialinfos)["Wert"]["Coil length"]
    
    Zeit_pro_Coil_Anode = meter_anodenkollektorfolie_pro_rolle/Geschwindigkeit_Anode #[min]
    Verlust_durch_Nebenzeit_Anode = df["Wert"]["Auxiliary process time anode"]/Zeit_pro_Coil_Anode #[%]
    
    Zeit_pro_Coil_Kathode = meter_kathodenkollektorfolie_pro_rolle/Geschwindigkeit_Kathode
    Verlust_durch_Nebenzeit_Kathode = float(df["Wert"]["Auxiliary process time cathode"])/Zeit_pro_Coil_Kathode #[%]
    
    Anlagen_Anode = math.ceil(Meter_Anode_pro_Minute/Geschwindigkeit_Anode*(1+Verlust_durch_Nebenzeit_Anode))
    Anlagen_Kathode = math.ceil(Meter_Kathode_pro_Minute/Geschwindigkeit_Kathode*(1+Verlust_durch_Nebenzeit_Kathode))

    Anz_Maschinen = "{} Anode, {} Cathode".format(Anlagen_Anode,Anlagen_Kathode)

    process.Anlagen_Anode = Anlagen_Anode
    process.Anlagen_Kathode = Anlagen_Kathode

    schritt_dictionary["Number of machines"] = Anz_Maschinen

    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen_getrennt(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def PHEV2_flat_winding(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.fixausschuss(schritt_dictionary,rueckgewinnung)   
    
    laenge_anodensheet = Zellergebnisse["Wert"]["Anode coating"]*Zellergebnisse["Wert"]["Sheets/meter anode"]  
    Zellen_pro_Minute = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr/24/60 #[Zellen/min]

    Kapazitaet_Anlage = df["Wert"]["Winding speed"]/laenge_anodensheet #[Zellen/min]
    Zeit_pro_Zelle = 1/Kapazitaet_Anlage
    Zeit_pro_Zelle_mit_nebenzeit = Zeit_pro_Zelle+df["Wert"]["Auxiliary process time"]
    Kapazitaet_Anlage_mit_nebenzeit = 1/Zeit_pro_Zelle_mit_nebenzeit

    process.Anlagen = math.ceil(Zellen_pro_Minute/Kapazitaet_Anlage_mit_nebenzeit)

    schritt_dictionary["Skilled workers"] = process.Anlagen*df["Wert"]["Specialists"]
    schritt_dictionary["Assistants"] = process.Anlagen*df["Wert"]["Support staff"]
    schritt_dictionary["Energy demand"] = process.Anlagen*df["Wert"]["Power consumption"]*process.arbeitstage_pro_jahr*24

    process.Anlagen = math.ceil(process.Anlagen * (1+df["Wert"]["Excess capacity"]/100))

    schritt_dictionary["Number of machines"] = process.Anlagen
    schritt_dictionary["Space requirements normal room"] = (process.Anlagen*df["Wert"]["Required space regular conditions"])/process.anteil_anlagengrundflaeche
    schritt_dictionary["Space requirements for dry room"] = (process.Anlagen*df["Wert"]["Required space dry room"])/process.anteil_anlagengrundflaeche

    schritt_dictionary["Investment"] = process.Anlagen*df["Wert"]["Investment"]

    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Separator")
    schritt_dictionary["Space requirement laboratory"] = 0

    return schritt_dictionary

def PHEV2_inserting_the_flat_pack_and_closing_of_lid(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)    
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Case")
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def PHEV2_contacting(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)    
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary
def PHEV2_electrolyte_filling(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    
    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr
    Zellen_pro_Minute = Zellen_pro_Tag/(24*60) 
    Zellen_pro_Minute = 1/(1/Zellen_pro_Minute+df["Wert"]["Auxiliary process time"])
    Durchsatz_pro_Minute = float(df["Wert"]["Number of cells processed in parallel"])*float(df["Wert"]["Operating speed"])
    process.Anlagen = math.ceil(Zellen_pro_Minute/Durchsatz_pro_Minute)
    schritt_dictionary["Number of machines"] = process.Anlagen
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Electrolyte")
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def PHEV2_wetting(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    
    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr
    Zellen_pro_Minute = Zellen_pro_Tag/(24*60) 
    Zellen_pro_Minute = 1/(1/Zellen_pro_Minute+df["Wert"]["Auxiliary process time"])
    Durchsatz_pro_Minute = 1/(float(df["Wert"]["Wetting time"])*60/float(df["Wert"]["Number of cells per machine"]))
    process.Anlagen = math.ceil(Zellen_pro_Minute/Durchsatz_pro_Minute)
    schritt_dictionary["Number of machines"] = process.Anlagen
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def PHEV2_forming_and_degassing(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)

    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)

    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr
    Zellen_pro_Minute = Zellen_pro_Tag/(24*60) 
    Zellen_pro_Minute = 1/(1/Zellen_pro_Minute+float(df["Wert"]["Auxiliary process time"]))
    Durchsatz_pro_Minute = 1/(float(df["Wert"]["Formation time"])*60/float(df["Wert"]["Number of cells per machine"]))
    process.Anlagen = math.ceil(Zellen_pro_Minute/Durchsatz_pro_Minute)

    rueckgewinnungsfaktor = df["Wert"]["Recovery factor"]

    Q_Z=float(Zellergebnisse["Wert"]["Capacity"]) #Speicherkapazität der Batteriezelle [Ah]
    U_OCV=float(Zellergebnisse["Wert"]["Nominal voltage"]) #Klemmspannung [Volt]
    Eta_C1=float(df["Wert"]["Eta C1"]) #Coulombscher Wirkungsgrad des ersten Ladezyklus [-]
    Eta_Z=float(df["Wert"]["Eta Z"]) #Wirkungsgrad der Zelle [-]
    
    E_L1=Q_Z*U_OCV/(Eta_C1*Eta_Z) #Energiebedarf des 1. Ladevorgangs [Wh]
    E_E1=Q_Z*U_OCV #Energiebedarf des 1. Entladevorgangs [Wh]
    E_L2=Q_Z*U_OCV/Eta_Z #Energiebedarf des 2. Ladevorgangs [Wh]
    E_E2=Q_Z*U_OCV #Energiebedarf des 2. Entladevorgangs [Wh]
    E_L50=0.5*Q_Z*U_OCV/Eta_Z #Energiebedarf des letzten Ladevorgangs auf 50% SOC [Wh]
    E_FormZ=E_L1+E_L2+E_L50-(E_E1+E_E2)*rueckgewinnungsfaktor/100 #Energiebedarf Formierung einer Zelle [Wh]

    kanaele_3_monats_test = df["Wert"]["Samples per shift 3 month test"] *3*3*30 #3 Schichten pro Tag * 3 Monate * 30 Tage
    kanaele_6_monats_test = df["Wert"]["Samples per shift 6 month test"] *3*6*30 #3 Schichten pro Tag * 6 Monate * 30 Tage
    kanaele_80_cutoff_test = df["Wert"]["Samples per shift cutoff"]*3 * 2/df["Wert"]["C-Rate Lifetime Test"]*df["Wert"]["Number of cycles"]/24
    lebensdauer_kanaele_gesamt = kanaele_3_monats_test + kanaele_6_monats_test + kanaele_80_cutoff_test
    anzahl_test_anlagen = math.ceil(lebensdauer_kanaele_gesamt/ df["Wert"]["Number of cells per machine"])

    energiebedarf_lebensdauertest = lebensdauer_kanaele_gesamt * Q_Z * U_OCV * df["Wert"]["C-Rate Lifetime Test"] * 0.5 * (1-rueckgewinnungsfaktor/100)*365*24 #[Wh]
    schritt_dictionary["Number of machines"] = "{} Anlagen, {} Testanlagen".format(process.Anlagen,anzahl_test_anlagen)
    
    process.Anlagen = process.Anlagen + anzahl_test_anlagen
    schritt_dictionary["Number of machines"] = process.Anlagen
    

    schritt_dictionary["Energy demand"]=E_FormZ*schritt_dictionary["Cell equivalent"]/1000 + energiebedarf_lebensdauertest/1000 #[kWh]
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)    
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = process.Anlagen*df["Wert"]["Required space laboratory"]/process.anteil_anlagengrundflaeche
    
    return schritt_dictionary

def PHEV2_closing_the_filling_opening(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = process.Anlagen*df["Wert"]["Required space laboratory"]/process.anteil_anlagengrundflaeche
    
    return schritt_dictionary
    
def PHEV2_aging(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)

    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)

    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr
    Zellen_pro_Minute = Zellen_pro_Tag/(24*60) 
    Zellen_pro_Minute = 1/(1/Zellen_pro_Minute+float(df["Wert"]["Auxiliary process time"]))
    Durchsatz_pro_Minute = 1/(float(df["Wert"]["Aging duration"])*24*60/float(df["Wert"]["Number of cells per machine"]))
    process.Anlagen = math.ceil(Zellen_pro_Minute/Durchsatz_pro_Minute)
    schritt_dictionary["Number of machines"] = process.Anlagen

    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)    
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = process.Anlagen*df["Wert"]["Required space laboratory"]/process.anteil_anlagengrundflaeche
    
    return schritt_dictionary

def PHEV2_end_of_line_test(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)

    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = process.Anlagen*df["Wert"]["Required space laboratory"]/process.anteil_anlagengrundflaeche
    
    return schritt_dictionary

def PHEV2_material_handling_storage_and_shipping(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    schritt_dictionary["Number of machines"] = 0
    schritt_dictionary["Space requirements normal room"] = df["Wert"]["Required space regular conditions"]
    schritt_dictionary["Space requirements for dry room"] = df["Wert"]["Required space dry room"]
    schritt_dictionary["Space requirement laboratory"] = df["Wert"]["Required space laboratory"]
    schritt_dictionary["Skilled workers"] = df["Wert"]["Specialists"]
    schritt_dictionary["Assistants"] = df["Wert"]["Support staff"]
    schritt_dictionary["Energy demand"] = 0
    schritt_dictionary["Investment"] = df["Wert"]["Investment"]
    
    return schritt_dictionary


#Tesla 4680 Produktion

def Cylindrical_4680_mixing(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = suspension_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
        
    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr

    Liter_Anode_pro_Tag = Zellen_pro_Tag*Zellergebnisse["Wert"]["Weight of the anode coating"]/Zellergebnisse["Wert"]["Density of the anode coating"]*(1/(Zellchemie["Wert"]["Solid content of anode"]/100))/1000 #[l]
    Liter_Kathode_pro_Tag = Zellen_pro_Tag*Zellergebnisse["Wert"]["Weight of the cathode coating"]/Zellergebnisse["Wert"]["Density of the cathode coating"]*(1/(Zellchemie["Wert"]["Solid content of cathode"]/100))/1000 #[l]

    Anlagen_Anode = math.ceil((Liter_Anode_pro_Tag/float(df["Wert"]["Usable volume of mixer anode"]))*float(df["Wert"]["Mixing time per batch anode"])/(24*60))
    Anlagen_Kathode = math.ceil((Liter_Kathode_pro_Tag/float(df["Wert"]["Usable volume of mixer cathode"]))*float(df["Wert"]["Mixing time per batch cathode"])/(24*60))
    
    process.Anlagen_Anode = Anlagen_Anode
    process.Anlagen_Kathode = Anlagen_Kathode

    schritt_dictionary["Energy demand"] = (Anlagen_Anode*float(df["Wert"]["Power consumption per mixer anode"])+Anlagen_Kathode*float(df["Wert"]["Power consumption per mixer cathode"]))*24*process.arbeitstage_pro_jahr
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)

    process.Anlagen_Anode = process.Anlagen_Anode*(1+df["Wert"]["Excess capacity"]/100)
    process.Anlagen_Kathode = process.Anlagen_Kathode*(1+df["Wert"]["Excess capacity"]/100)

    Anlagen_Dosierer_Anode = math.ceil(Anlagen_Anode/float(df["Wert"]["Number of mixers per dosing unit (anode)"]))
    Anlagen_Dosierer_Kathode = math.ceil(Anlagen_Kathode/float(df["Wert"]["Number of mixers per dosing unit(cathode)"]))

    schritt_dictionary["Number of machines"] = "{} Mixer Anode, {} -Cathode, {} Dispenser Anode, {} -Cathode".format(Anlagen_Anode,Anlagen_Kathode,Anlagen_Dosierer_Anode,Anlagen_Dosierer_Kathode)

    Anzahl_Anlagen = Anlagen_Anode+Anlagen_Kathode
    
    schritt_dictionary["Investment"] =   Anlagen_Anode *float(df["Wert"]["Investment cost anode"]) +\
                    Anlagen_Kathode *float(df["Wert"]["Investment cost cathode"])+\
                    Anlagen_Dosierer_Anode*float(df["Wert"]["Investment cost dosing unit (anode)"])+\
                    Anlagen_Dosierer_Kathode*float(df["Wert"]["Investment cost dosing unit (cathode)"])
                    
    schritt_dictionary["Space requirements normal room"] = (process.Anlagen_Anode*float(df["Wert"]["Required space regular environment mixer anode"]) +\
                                          process.Anlagen_Kathode*float(df["Wert"]["Required space regular environment mixer cathode"]) +\
                                         (Anlagen_Dosierer_Anode+Anlagen_Dosierer_Kathode)*float(df["Wert"]["Required space regular environment dosing unit"]))/process.anteil_anlagengrundflaeche

    schritt_dictionary["Space requirements for dry room"] = (process.Anlagen_Anode*float(df["Wert"]["Required space dry room mixer anode"]) +\
                                          process.Anlagen_Kathode*float(df["Wert"]["Required space dry room mixer cathode"]) +\
                                         (Anlagen_Dosierer_Anode+Anlagen_Dosierer_Kathode)*float(df["Wert"]["Required space dry room dosing unit"]))/process.anteil_anlagengrundflaeche

    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Anode coating;Cathode coating")
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def Cylindrical_4680_coating_and_drying(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.fixausschuss(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen_coating_drying(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)

    Areal_loading_anode = Zellergebnisse["Wert"]["Areal mass of anode coating"]
    print(Areal_loading_anode)
    Areal_loading_cathode = Zellergebnisse["Wert"]["Areal mass of cathode coating"]
    print(Areal_loading_cathode)
    Drying_duration_anode = Zellergebnisse["Wert"]["Areal mass of anode coating"]*(1-(Zellchemie["Wert"]["Solid content of anode"]/100))/(Zellchemie["Wert"]["Solid content of anode"]/100)*(1/float(df["Wert"]["Drying rate"]))*10000/60/1000 #[minutes]
    print(Drying_duration_anode)
    Drying_duration_cathode = Zellergebnisse["Wert"]["Areal mass of cathode coating"]*(1-(Zellchemie["Wert"]["Solid content of cathode"]/100))/(Zellchemie["Wert"]["Solid content of cathode"]/100)*(1/float(df["Wert"]["Drying rate"]))*10000/60/1000 #[minutes]
    print(Drying_duration_cathode)

    Trocknerlänge_Anode = float(df["Wert"]["Coating speed anode"])*Drying_duration_anode #[m]
    Trocknerlänge_Kathode = float(df["Wert"]["Coating speed cathode"])*Drying_duration_cathode #[m]
    
    Anlagengrundfläche_Anode = df["Wert"]["Machine width"]*(df["Wert"]["Length of coating head"]+Trocknerlänge_Anode) #[m²]
    Anlagengrundfläche_Kathode = df["Wert"]["Machine width"]*(df["Wert"]["Length of coating head"]+Trocknerlänge_Kathode) #[m2]
    
    schritt_dictionary["Space requirements normal room"] = (Anlagengrundfläche_Anode*(1-float(df["Wert"]["Anode machines placed in dry room"]))*process.Anlagen_Anode+\
                                          Anlagengrundfläche_Kathode*(1-float(df["Wert"]["Cathode machines placed in dry room"]))*process.Anlagen_Kathode)/process.anteil_anlagengrundflaeche #[m²]

    schritt_dictionary["Space requirements for dry room"]  = (Anlagengrundfläche_Anode*(float(df["Wert"]["Anode machines placed in dry room"]))*process.Anlagen_Anode+\
                                          Anlagengrundfläche_Kathode*(float(df["Wert"]["Cathode machines placed in dry room"]))*process.Anlagen_Kathode)/process.anteil_anlagengrundflaeche #[m²]
    schritt_dictionary["Number of machines"] = process.Anlagen_Anode+process.Anlagen_Kathode
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Anode collector;Cathode collector")
    schritt_dictionary["Space requirement laboratory"] = 0

    return schritt_dictionary

def Cylindrical_4680_calendering(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen_calendering(schritt_dictionary)   
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen_getrennt(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0

    return schritt_dictionary

def Cylindrical_4680_slitting(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen_slitting(schritt_dictionary)   
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen_getrennt(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def Cylindrical_4680_post_drying(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.fixausschuss(schritt_dictionary,rueckgewinnung)

    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr

    Anodenkollektorfolie = Zellchemie.loc[Zellchemie['Kategorie'] == "Collector foil anode"].index.tolist()[0]
    Kathodenkollektorfolie = Zellchemie.loc[Zellchemie['Kategorie'] == "Collector foil cathode"].index.tolist()[0]

    Meter_Anode_pro_Tag = Zellen_pro_Tag*Zellergebnisse["Wert"]["Number of repeating units"]/Zellergebnisse["Wert"]["Sheets/meter anode"] #[m]
    Meter_Kathode_pro_Tag = Zellen_pro_Tag*Zellergebnisse["Wert"]["Number of repeating units"]/Zellergebnisse["Wert"]["Sheets/meter cathode"] #[m]

    Meter_Anode_pro_Minute = Meter_Anode_pro_Tag/(24*60)
    Meter_Kathode_pro_Minute = Meter_Kathode_pro_Tag/(24*60)

    Geschwindigkeit_Anode = float(df["Wert"]["Throughput anode"])/(read_zellinfo(Anodenkollektorfolie,Materialinfos)["Wert"]["Width"]/1000)/(8*60)
    Geschwindigkeit_Kathode = float(df["Wert"]["Throughput cathode"])/(read_zellinfo(Kathodenkollektorfolie,Materialinfos)["Wert"]["Width"]/1000)/(8*60)
    
    meter_anodenkollektorfolie_pro_rolle = read_zellinfo(Anodenkollektorfolie,Materialinfos)["Wert"]["Coil length"]
    meter_kathodenkollektorfolie_pro_rolle = read_zellinfo(Kathodenkollektorfolie,Materialinfos)["Wert"]["Coil length"]
    
    Zeit_pro_Coil_Anode = meter_anodenkollektorfolie_pro_rolle/Geschwindigkeit_Anode #[min]
    Verlust_durch_Nebenzeit_Anode = df["Wert"]["Auxiliary process time anode"]/Zeit_pro_Coil_Anode #[%]
    
    Zeit_pro_Coil_Kathode = meter_kathodenkollektorfolie_pro_rolle/Geschwindigkeit_Kathode
    Verlust_durch_Nebenzeit_Kathode = float(df["Wert"]["Auxiliary process time cathode"])/Zeit_pro_Coil_Kathode #[%]
    
    Anlagen_Anode = math.ceil(Meter_Anode_pro_Minute/Geschwindigkeit_Anode*(1+Verlust_durch_Nebenzeit_Anode))
    Anlagen_Kathode = math.ceil(Meter_Kathode_pro_Minute/Geschwindigkeit_Kathode*(1+Verlust_durch_Nebenzeit_Kathode))

    Anz_Maschinen = "{} Anode, {} Cathode".format(Anlagen_Anode,Anlagen_Kathode)

    process.Anlagen_Anode = Anlagen_Anode
    process.Anlagen_Kathode = Anlagen_Kathode

    schritt_dictionary["Number of machines"] = Anz_Maschinen

    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen_getrennt(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary


def Cylindrical_4680_winding(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.fixausschuss(schritt_dictionary,rueckgewinnung)   
    
    laenge_anodensheet = Zellergebnisse["Wert"]["Anode coating"]/Zellergebnisse["Wert"]["Sheets/meter anode"]
    Zellen_pro_Minute = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr/24/60 #[Zellen/min]

    Kapazitaet_Anlage = df["Wert"]["Winding speed"]/laenge_anodensheet #[Zellen/min]
    Zeit_pro_Zelle = 1/Kapazitaet_Anlage
    Zeit_pro_Zelle_mit_nebenzeit = Zeit_pro_Zelle+df["Wert"]["Auxiliary process time"]
    Kapazitaet_Anlage_mit_nebenzeit = 1/Zeit_pro_Zelle_mit_nebenzeit

    process.Anlagen = math.ceil(Zellen_pro_Minute/Kapazitaet_Anlage_mit_nebenzeit)

    schritt_dictionary["Skilled workers"] = process.Anlagen*df["Wert"]["Specialists"]
    schritt_dictionary["Assistants"] = process.Anlagen*df["Wert"]["Support staff"]
    schritt_dictionary["Energy demand"] = process.Anlagen*df["Wert"]["Power consumption"]*process.arbeitstage_pro_jahr*24

    process.Anlagen = math.ceil(process.Anlagen * (1+df["Wert"]["Excess capacity"]/100))

    schritt_dictionary["Number of machines"] = process.Anlagen
    schritt_dictionary["Space requirements normal room"] = process.Anlagen*df["Wert"]["Required space regular conditions"]
    schritt_dictionary["Space requirements for dry room"] = process.Anlagen*df["Wert"]["Required space dry room"]

    schritt_dictionary["Investment"] = process.Anlagen*df["Wert"]["Investment"]

    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Separator")
    schritt_dictionary["Space requirement laboratory"] = 0

    return schritt_dictionary

def Cylindrical_4680_inserting_jelly_roll_and_closing_of_lid(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)    
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Case")
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def Cylindrical_4680_contacting(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)    
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary


def Cylindrical_4680_electrolyte_filling(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    
    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr
    Zellen_pro_Minute = Zellen_pro_Tag/(24*60) 
    Zellen_pro_Minute = 1/(1/Zellen_pro_Minute+df["Wert"]["Auxiliary process time"])
    Durchsatz_pro_Minute = float(df["Wert"]["Number of cells processed in parallel"])*float(df["Wert"]["Operating speed"])
    process.Anlagen = math.ceil(Zellen_pro_Minute/Durchsatz_pro_Minute)

    schritt_dictionary["Number of machines"] = process.Anlagen
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Electrolyte")
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def Cylindrical_4680_wetting(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    
    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr
    Zellen_pro_Minute = Zellen_pro_Tag/(24*60) 
    Zellen_pro_Minute = 1/(1/Zellen_pro_Minute+df["Wert"]["Auxiliary process time"])
    Durchsatz_pro_Minute = 1/(float(df["Wert"]["Wetting time"])*60/float(df["Wert"]["Number of cells per machine"]))
    process.Anlagen = math.ceil(Zellen_pro_Minute/Durchsatz_pro_Minute)

    schritt_dictionary["Number of machines"] = process.Anlagen
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def Cylindrical_4680_forming_and_degassing(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)

    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)

    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr
    Zellen_pro_Minute = Zellen_pro_Tag/(24*60) 
    Zellen_pro_Minute = 1/(1/Zellen_pro_Minute+float(df["Wert"]["Auxiliary process time"]))
    Durchsatz_pro_Minute = 1/(float(df["Wert"]["Formation time"])*60/float(df["Wert"]["Number of cells per machine"]))
    process.Anlagen = math.ceil(Zellen_pro_Minute/Durchsatz_pro_Minute)

    rueckgewinnungsfaktor = df["Wert"]["Recovery factor"]

    Q_Z=float(Zellergebnisse["Wert"]["Capacity"]) #Speicherkapazität der Batteriezelle [Ah]
    U_OCV=float(Zellergebnisse["Wert"]["Nominal voltage"]) #Klemmspannung [Volt]
    Eta_C1=float(df["Wert"]["Eta C1"]) #Coulombscher Wirkungsgrad des ersten Ladezyklus [-]
    Eta_Z=float(df["Wert"]["Eta Z"]) #Wirkungsgrad der Zelle [-]
    
    E_L1=Q_Z*U_OCV/(Eta_C1*Eta_Z) #Energiebedarf des 1. Ladevorgangs [Wh]
    E_E1=Q_Z*U_OCV #Energiebedarf des 1. Entladevorgangs [Wh]
    E_L2=Q_Z*U_OCV/Eta_Z #Energiebedarf des 2. Ladevorgangs [Wh]
    E_E2=Q_Z*U_OCV #Energiebedarf des 2. Entladevorgangs [Wh]
    E_L50=0.5*Q_Z*U_OCV/Eta_Z #Energiebedarf des letzten Ladevorgangs auf 50% SOC [Wh]
    E_FormZ=E_L1+E_L2+E_L50-(E_E1+E_E2)*rueckgewinnungsfaktor/100 #Energiebedarf Formierung einer Zelle [Wh]

    kanaele_3_monats_test = df["Wert"]["Samples per shift 3 month test"] *3*3*30 #3 Schichten pro Tag * 3 Monate * 30 Tage
    kanaele_6_monats_test = df["Wert"]["Samples per shift 6 month test"] *3*6*30 #3 Schichten pro Tag * 6 Monate * 30 Tage
    kanaele_80_cutoff_test = df["Wert"]["Samples per shift cutoff"]*3 * 2/df["Wert"]["C-Rate Lifetime Test"]*df["Wert"]["Number of cycles"]/24
    lebensdauer_kanaele_gesamt = kanaele_3_monats_test + kanaele_6_monats_test + kanaele_80_cutoff_test
    anzahl_test_anlagen = math.ceil(lebensdauer_kanaele_gesamt/ df["Wert"]["Number of cells per machine"])
    #print("anzahl_test_anlagen")
    #print(anzahl_test_anlagen)
    energiebedarf_lebensdauertest = lebensdauer_kanaele_gesamt * Q_Z * U_OCV * df["Wert"]["C-Rate Lifetime Test"] * 0.5 * (1-rueckgewinnungsfaktor/100)*365*24 #[Wh]

    process.Anlagen = process.Anlagen + anzahl_test_anlagen

    schritt_dictionary["Number of machines"] = process.Anlagen
    schritt_dictionary["Energy demand"]=E_FormZ*schritt_dictionary["Cell equivalent"]/1000 + energiebedarf_lebensdauertest/1000 #[kWh]
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)    
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = process.Anlagen*df["Wert"]["Required space laboratory"]/process.anteil_anlagengrundflaeche
    
    return schritt_dictionary

def Cylindrical_4680_closing_the_filling_opening(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = process.Anlagen*df["Wert"]["Required space laboratory"]/process.anteil_anlagengrundflaeche
    
    return schritt_dictionary
    
def Cylindrical_4680_aging(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)

    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)

    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr
    Zellen_pro_Minute = Zellen_pro_Tag/(24*60) 
    Zellen_pro_Minute = 1/(1/Zellen_pro_Minute+float(df["Wert"]["Auxiliary process time"]))
    Durchsatz_pro_Minute = 1/(float(df["Wert"]["Aging duration"])*24*60/float(df["Wert"]["Number of cells per machine"]))
    process.Anlagen = math.ceil(Zellen_pro_Minute/Durchsatz_pro_Minute)

    schritt_dictionary["Number of machines"] = process.Anlagen
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)    
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = process.Anlagen*df["Wert"]["Required space laboratory"]/process.anteil_anlagengrundflaeche
    
    return schritt_dictionary

def Cylindrical_4680_end_of_line_test(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = process.Anlagen*df["Wert"]["Required space laboratory"]/process.anteil_anlagengrundflaeche
    
    return schritt_dictionary

def Cylindrical_4680_material_handling_storage_and_shipping(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    schritt_dictionary["Number of machines"] = 0
    schritt_dictionary["Space requirements normal room"] = df["Wert"]["Required space regular conditions"]
    schritt_dictionary["Space requirements for dry room"] = df["Wert"]["Required space dry room"]
    schritt_dictionary["Space requirement laboratory"] = df["Wert"]["Required space laboratory"]
    schritt_dictionary["Skilled workers"] = df["Wert"]["Specialists"]
    schritt_dictionary["Assistants"] = df["Wert"]["Support staff"]
    schritt_dictionary["Energy demand"] = 0
    schritt_dictionary["Investment"] = df["Wert"]["Investment"]
    
    return schritt_dictionary

#LFP-PHEV 2 Produktion

def LFP_PHEV2_mixing(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = suspension_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
     
    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr

    Liter_Anode_pro_Tag = Zellen_pro_Tag*Zellergebnisse["Wert"]["Weight of the anode coating"]/Zellergebnisse["Wert"]["Density of the anode coating"]*(1/(Zellchemie["Wert"]["Solid content of anode"]/100))/1000 #[l]
    Liter_Kathode_pro_Tag = Zellen_pro_Tag*Zellergebnisse["Wert"]["Weight of the cathode coating"]/Zellergebnisse["Wert"]["Density of the cathode coating"]*(1/(Zellchemie["Wert"]["Solid content of cathode"]/100))/1000 #[l]

    Anlagen_Anode = math.ceil((Liter_Anode_pro_Tag/float(df["Wert"]["Usable volume of mixer anode"]))*float(df["Wert"]["Mixing time per batch anode"])/(24*60))
    Anlagen_Kathode = math.ceil((Liter_Kathode_pro_Tag/float(df["Wert"]["Usable volume of mixer cathode"]))*float(df["Wert"]["Mixing time per batch cathode"])/(24*60))
    
    process.Anlagen_Anode = Anlagen_Anode
    process.Anlagen_Kathode = Anlagen_Kathode

    schritt_dictionary["Energy demand"] = (Anlagen_Anode*float(df["Wert"]["Power consumption per mixer anode"])+Anlagen_Kathode*float(df["Wert"]["Power consumption per mixer cathode"]))*24*process.arbeitstage_pro_jahr
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)

    process.Anlagen_Anode = math.ceil(process.Anlagen_Anode*(1+df["Wert"]["Excess capacity"]/100))
    process.Anlagen_Kathode = math.ceil(process.Anlagen_Kathode*(1+df["Wert"]["Excess capacity"]/100))

    Anlagen_Dosierer_Anode = math.ceil(Anlagen_Anode/float(df["Wert"]["Number of mixers per dosing unit (anode)"]))
    Anlagen_Dosierer_Kathode = math.ceil(Anlagen_Kathode/float(df["Wert"]["Number of mixers per dosing unit(cathode)"]))

    schritt_dictionary["Number of machines"] = "{} Mixer Anode, {} -Cathode, {} Dispenser Anode, {} -Cathode".format(Anlagen_Anode,Anlagen_Kathode,Anlagen_Dosierer_Anode,Anlagen_Dosierer_Kathode)
    
    schritt_dictionary["Investment"] =   Anlagen_Anode *float(df["Wert"]["Investment cost anode"]) +\
                    Anlagen_Kathode *float(df["Wert"]["Investment cost cathode"])+\
                    Anlagen_Dosierer_Anode*float(df["Wert"]["Investment cost dosing unit (anode)"])+\
                    Anlagen_Dosierer_Kathode*float(df["Wert"]["Investment cost dosing unit (cathode)"])
                    
    schritt_dictionary["Space requirements normal room"] = (process.Anlagen_Anode*float(df["Wert"]["Required space regular environment mixer anode"]) +\
                                          process.Anlagen_Kathode*float(df["Wert"]["Required space regular environment mixer cathode"]) +\
                                         (Anlagen_Dosierer_Anode+Anlagen_Dosierer_Kathode)*float(df["Wert"]["Required space regular environment dosing unit"]))/process.anteil_anlagengrundflaeche

    schritt_dictionary["Space requirements for dry room"] = (process.Anlagen_Anode*float(df["Wert"]["Required space dry room mixer anode"]) +\
                                          process.Anlagen_Kathode*float(df["Wert"]["Required space dry room mixer cathode"]) +\
                                         (Anlagen_Dosierer_Anode+Anlagen_Dosierer_Kathode)*float(df["Wert"]["Required space dry room dosing unit"]))/process.anteil_anlagengrundflaeche

    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Anode coating;Cathode coating")
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary


def LFP_PHEV2_coating_and_drying(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.fixausschuss(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen_coating_drying(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)

    Drying_duration_anode = Zellergebnisse["Wert"]["Areal mass of anode coating"]*(1-(Zellchemie["Wert"]["Solid content of anode"]/100))/(Zellchemie["Wert"]["Solid content of anode"]/100)*(1/float(df["Wert"]["Drying rate"]))*10000/60/1000 #[min]
    print(Drying_duration_anode)
    Drying_duration_cathode = Zellergebnisse["Wert"]["Areal mass of cathode coating"]*(1-(Zellchemie["Wert"]["Solid content of cathode"]/100))/(Zellchemie["Wert"]["Solid content of cathode"]/100)*(1/float(df["Wert"]["Drying rate"]))*10000/60/1000 #[min]
    print(Drying_duration_cathode)

    Trocknerlänge_Anode = float(df["Wert"]["Coating speed anode"])*Drying_duration_anode #[m]
    Trocknerlänge_Kathode = float(df["Wert"]["Coating speed cathode"])*Drying_duration_cathode #[m]
    
    Anlagengrundfläche_Anode = df["Wert"]["Machine width"]*(df["Wert"]["Length of coating head"]+Trocknerlänge_Anode) #[m²]
    Anlagengrundfläche_Kathode = df["Wert"]["Machine width"]*(df["Wert"]["Length of coating head"]+Trocknerlänge_Kathode) #[m2]
    
    schritt_dictionary["Space requirements normal room"] = (Anlagengrundfläche_Anode*(1-float(df["Wert"]["Anode machines placed in dry room"]))*process.Anlagen_Anode+\
                                          Anlagengrundfläche_Kathode*(1-float(df["Wert"]["Cathode machines placed in dry room"]))*process.Anlagen_Kathode)/process.anteil_anlagengrundflaeche #[m²]

    schritt_dictionary["Space requirements for dry room"]  = (Anlagengrundfläche_Anode*(float(df["Wert"]["Anode machines placed in dry room"]))*process.Anlagen_Anode+\
                                          Anlagengrundfläche_Kathode*(float(df["Wert"]["Cathode machines placed in dry room"]))*process.Anlagen_Kathode)/process.anteil_anlagengrundflaeche #[m²]
    schritt_dictionary["Number of machines"] = process.Anlagen_Anode+process.Anlagen_Kathode
    schritt_dictionary = process.investition(schritt_dictionary)
    
    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Anode collector;Cathode collector")
    schritt_dictionary["Space requirement laboratory"] = 0

    return schritt_dictionary

def LFP_PHEV2_calendering(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen_calendering(schritt_dictionary)   
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen_getrennt(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def LFP_PHEV2_slitting(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.fixausschuss(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen_slitting(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen_getrennt(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def LFP_PHEV2_post_drying(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.fixausschuss(schritt_dictionary,rueckgewinnung)
    #schritt_dictionary = process.anlagen(schritt_dictionary)

    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr

    Anodenkollektorfolie = Zellchemie.loc[Zellchemie['Kategorie'] == "Collector foil anode"].index.tolist()[0]
    Kathodenkollektorfolie = Zellchemie.loc[Zellchemie['Kategorie'] == "Collector foil cathode"].index.tolist()[0]

    Meter_Anode_pro_Tag = Zellen_pro_Tag*Zellergebnisse["Wert"]["Number of repeating units"]/Zellergebnisse["Wert"]["Sheets/meter anode"] #[m]
    Meter_Kathode_pro_Tag = Zellen_pro_Tag*Zellergebnisse["Wert"]["Number of repeating units"]/Zellergebnisse["Wert"]["Sheets/meter cathode"] #[m]

    Meter_Anode_pro_Minute = Meter_Anode_pro_Tag/(24*60)
    Meter_Kathode_pro_Minute = Meter_Kathode_pro_Tag/(24*60)

    Geschwindigkeit_Anode = float(df["Wert"]["Throughput anode"])/(read_zellinfo(Anodenkollektorfolie,Materialinfos)["Wert"]["Width"]/1000)/(8*60)
    Geschwindigkeit_Kathode = float(df["Wert"]["Throughput cathode"])/(read_zellinfo(Kathodenkollektorfolie,Materialinfos)["Wert"]["Width"]/1000)/(8*60)
    
    meter_anodenkollektorfolie_pro_rolle = read_zellinfo(Anodenkollektorfolie,Materialinfos)["Wert"]["Coil length"]
    meter_kathodenkollektorfolie_pro_rolle = read_zellinfo(Kathodenkollektorfolie,Materialinfos)["Wert"]["Coil length"]
    
    Zeit_pro_Coil_Anode = meter_anodenkollektorfolie_pro_rolle/Geschwindigkeit_Anode #[min]
    Verlust_durch_Nebenzeit_Anode = df["Wert"]["Auxiliary process time anode"]/Zeit_pro_Coil_Anode #[%]
    
    Zeit_pro_Coil_Kathode = meter_kathodenkollektorfolie_pro_rolle/Geschwindigkeit_Kathode
    Verlust_durch_Nebenzeit_Kathode = float(df["Wert"]["Auxiliary process time cathode"])/Zeit_pro_Coil_Kathode #[%]
    
    Anlagen_Anode = math.ceil(Meter_Anode_pro_Minute/Geschwindigkeit_Anode*(1+Verlust_durch_Nebenzeit_Anode))
    Anlagen_Kathode = math.ceil(Meter_Kathode_pro_Minute/Geschwindigkeit_Kathode*(1+Verlust_durch_Nebenzeit_Kathode))

    Anz_Maschinen = "{} Anode, {} Cathode".format(Anlagen_Anode,Anlagen_Kathode)

    process.Anlagen_Anode = Anlagen_Anode
    process.Anlagen_Kathode = Anlagen_Kathode

    schritt_dictionary["Number of machines"] = Anz_Maschinen

    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen_getrennt(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def LFP_PHEV2_flat_winding(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = coil_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.fixausschuss(schritt_dictionary,rueckgewinnung)   
    
    #laenge_anodensheet = Zellergebnisse["Wert"]["Sheets/ Meter Anode"]*Zellergebnisse["Wert"]["Beschichtete Bahnen Anode"] #[m/Zelle]
    laenge_anodensheet = Zellergebnisse["Wert"]["Anode coating"]*Zellergebnisse["Wert"]["Sheets/meter anode"]  
    Zellen_pro_Minute = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr/24/60 #[Zellen/min]

    #Meter_Anode_pro_minute = laenge_anodensheet * Zellen_pro_Minute #[m/min]
    Kapazitaet_Anlage = df["Wert"]["Winding speed"]/laenge_anodensheet #[Zellen/min]
    Zeit_pro_Zelle = 1/Kapazitaet_Anlage
    Zeit_pro_Zelle_mit_nebenzeit = Zeit_pro_Zelle+df["Wert"]["Auxiliary process time"]
    Kapazitaet_Anlage_mit_nebenzeit = 1/Zeit_pro_Zelle_mit_nebenzeit

    process.Anlagen = math.ceil(Zellen_pro_Minute/Kapazitaet_Anlage_mit_nebenzeit)

    schritt_dictionary["Skilled workers"] = process.Anlagen*df["Wert"]["Specialists"]
    schritt_dictionary["Assistants"] = process.Anlagen*df["Wert"]["Support staff"]
    schritt_dictionary["Energy demand"] = process.Anlagen*df["Wert"]["Power consumption"]*process.arbeitstage_pro_jahr*24

    process.Anlagen = math.ceil(process.Anlagen * (1+df["Wert"]["Excess capacity"]/100))

    schritt_dictionary["Number of machines"] = process.Anlagen
    schritt_dictionary["Space requirements normal room"] = (process.Anlagen*df["Wert"]["Required space regular conditions"])/process.anteil_anlagengrundflaeche
    schritt_dictionary["Space requirements for dry room"] = (process.Anlagen*df["Wert"]["Required space dry room"])/process.anteil_anlagengrundflaeche

    schritt_dictionary["Investment"] = process.Anlagen*df["Wert"]["Investment"]

    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Separator")
    schritt_dictionary["Space requirement laboratory"] = 0

    return schritt_dictionary

def LFP_PHEV2_inserting_the_flat_pack_and_closing_of_lid(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)    
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Case")
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def LFP_PHEV2_contacting(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)    
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary
def LFP_PHEV2_electrolyte_filling(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    
    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr
    Zellen_pro_Minute = Zellen_pro_Tag/(24*60) 
    Zellen_pro_Minute = 1/(1/Zellen_pro_Minute+df["Wert"]["Auxiliary process time"])
    Durchsatz_pro_Minute = float(df["Wert"]["Number of cells processed in parallel"])*float(df["Wert"]["Operating speed"])
    process.Anlagen = math.ceil(Zellen_pro_Minute/Durchsatz_pro_Minute)
    schritt_dictionary["Number of machines"] = process.Anlagen
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary,"Electrolyte")
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def LFP_PHEV2_wetting(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    
    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr
    Zellen_pro_Minute = Zellen_pro_Tag/(24*60) 
    Zellen_pro_Minute = 1/(1/Zellen_pro_Minute+df["Wert"]["Auxiliary process time"])
    Durchsatz_pro_Minute = 1/(float(df["Wert"]["Wetting time"])*60/float(df["Wert"]["Number of cells per machine"]))
    process.Anlagen = math.ceil(Zellen_pro_Minute/Durchsatz_pro_Minute)
    schritt_dictionary["Number of machines"] = process.Anlagen
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = 0
    
    return schritt_dictionary

def LFP_PHEV2_forming_and_degassing(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)

    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)

    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr
    Zellen_pro_Minute = Zellen_pro_Tag/(24*60) 
    Zellen_pro_Minute = 1/(1/Zellen_pro_Minute+float(df["Wert"]["Auxiliary process time"]))
    Durchsatz_pro_Minute = 1/(float(df["Wert"]["Formation time"])*60/float(df["Wert"]["Number of cells per machine"]))
    process.Anlagen = math.ceil(Zellen_pro_Minute/Durchsatz_pro_Minute)

    rueckgewinnungsfaktor = df["Wert"]["Recovery factor"]

    Q_Z=float(Zellergebnisse["Wert"]["Capacity"]) #Speicherkapazität der Batteriezelle [Ah]
    U_OCV=float(Zellergebnisse["Wert"]["Nominal voltage"]) #Klemmspannung [Volt]
    Eta_C1=float(df["Wert"]["Eta C1"]) #Coulombscher Wirkungsgrad des ersten Ladezyklus [-]
    Eta_Z=float(df["Wert"]["Eta Z"]) #Wirkungsgrad der Zelle [-]
    
    E_L1=Q_Z*U_OCV/(Eta_C1*Eta_Z) #Energiebedarf des 1. Ladevorgangs [Wh]
    E_E1=Q_Z*U_OCV #Energiebedarf des 1. Entladevorgangs [Wh]
    E_L2=Q_Z*U_OCV/Eta_Z #Energiebedarf des 2. Ladevorgangs [Wh]
    E_E2=Q_Z*U_OCV #Energiebedarf des 2. Entladevorgangs [Wh]
    E_L50=0.5*Q_Z*U_OCV/Eta_Z #Energiebedarf des letzten Ladevorgangs auf 50% SOC [Wh]
    E_FormZ=E_L1+E_L2+E_L50-(E_E1+E_E2)*rueckgewinnungsfaktor/100 #Energiebedarf Formierung einer Zelle [Wh]

    kanaele_3_monats_test = df["Wert"]["Samples per shift 3 month test"] *3*3*30 #3 Schichten pro Tag (HARDCODED) * 3 Monate * 30 Tage
    kanaele_6_monats_test = df["Wert"]["Samples per shift 6 month test"] *3*6*30 #3 Schichten pro Tag (HARDCODED) * 6 Monate * 30 Tage
    #kanaele_80_cutoff_test = df["Wert"]["Stichproben pro Schicht Cutoff"] * 2/df["Wert"]["C-Rate Lebensdauertest"]*df["Wert"]["Zyklenzahl"]/24
    kanaele_80_cutoff_test = df["Wert"]["Samples per shift cutoff"]*3 * 2/df["Wert"]["C-Rate Lifetime Test"]*df["Wert"]["Number of cycles"]/24
    lebensdauer_kanaele_gesamt = kanaele_3_monats_test + kanaele_6_monats_test + kanaele_80_cutoff_test
    anzahl_test_anlagen = math.ceil(lebensdauer_kanaele_gesamt/ df["Wert"]["Number of cells per machine"])

    energiebedarf_lebensdauertest = lebensdauer_kanaele_gesamt * Q_Z * U_OCV * df["Wert"]["C-Rate Lifetime Test"] * 0.5 * (1-rueckgewinnungsfaktor/100)*365*24 #[Wh]
    schritt_dictionary["Number of machines"] = "{} Anlagen, {} Testanlagen".format(process.Anlagen,anzahl_test_anlagen)
    
    process.Anlagen = process.Anlagen + anzahl_test_anlagen
    schritt_dictionary["Number of machines"] = process.Anlagen
    

    schritt_dictionary["Energy demand"]=E_FormZ*schritt_dictionary["Cell equivalent"]/1000 + energiebedarf_lebensdauertest/1000 #[kWh]
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)    
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = process.Anlagen*df["Wert"]["Required space laboratory"]/process.anteil_anlagengrundflaeche
    
    return schritt_dictionary

def LFP_PHEV2_closing_the_filling_opening(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)
    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = process.Anlagen*df["Wert"]["Required space laboratory"]/process.anteil_anlagengrundflaeche
    
    return schritt_dictionary
    
def LFP_PHEV2_aging(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)

    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)

    Zellen_pro_Tag = schritt_dictionary["Cell equivalent"]/process.arbeitstage_pro_jahr
    Zellen_pro_Minute = Zellen_pro_Tag/(24*60) 
    Zellen_pro_Minute = 1/(1/Zellen_pro_Minute+float(df["Wert"]["Auxiliary process time"]))
    Durchsatz_pro_Minute = 1/(float(df["Wert"]["Aging duration"])*24*60/float(df["Wert"]["Number of cells per machine"]))
    process.Anlagen = math.ceil(Zellen_pro_Minute/Durchsatz_pro_Minute)
    schritt_dictionary["Number of machines"] = process.Anlagen

    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)    
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = process.Anlagen*df["Wert"]["Required space laboratory"]/process.anteil_anlagengrundflaeche
    
    return schritt_dictionary

def LFP_PHEV2_end_of_line_test(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    process = zelle_prozessschritt(df,Zellergebnisse,Zellchemie,Materialinfos,rueckgewinnung,schritt_dictionary)

    schritt_dictionary = process.variabler_aussschuss(schritt_dictionary)
    schritt_dictionary = process.rueckgewinnung(schritt_dictionary,rueckgewinnung)
    schritt_dictionary = process.anlagen(schritt_dictionary)
    schritt_dictionary = process.mitarbeiter_anlagen(schritt_dictionary)
    schritt_dictionary = process.energie(schritt_dictionary)
    schritt_dictionary = process.ueberkapazitaet(schritt_dictionary)
    schritt_dictionary = process.flaechen(schritt_dictionary)
    schritt_dictionary = process.investition(schritt_dictionary)
    schritt_dictionary = process.neue_materialien(schritt_dictionary)
    schritt_dictionary["Space requirement laboratory"] = process.Anlagen*df["Wert"]["Required space laboratory"]/process.anteil_anlagengrundflaeche
    
    return schritt_dictionary

def LFP_PHEV2_material_handling_storage_and_shipping(df,Zellergebnisse,Zellchemie,Materialinfos,schritt_dictionary,rueckgewinnung):
    schritt_dictionary["Number of machines"] = 0
    schritt_dictionary["Space requirements normal room"] = df["Wert"]["Required space regular conditions"]
    schritt_dictionary["Space requirements for dry room"] = df["Wert"]["Required space dry room"]
    schritt_dictionary["Space requirement laboratory"] = df["Wert"]["Required space laboratory"]
    schritt_dictionary["Skilled workers"] = df["Wert"]["Specialists"]
    schritt_dictionary["Assistants"] = df["Wert"]["Support staff"]
    schritt_dictionary["Energy demand"] = 0
    schritt_dictionary["Investment"] = df["Wert"]["Investment"]
    
    return schritt_dictionary

