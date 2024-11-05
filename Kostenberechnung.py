# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 18:06:34 2022

@1st author: bendzuck
@2nd author: mahin
"""
import pandas as pd
import json
import math
import copy
import Prozessfunktionen
from Flaechenberechnung import flaechenberechnung
from levelized_cost_calculation import levelized_cost

def Kostenberechnung(Zellergebnisse_raw,
                     Zellchemie_raw,
                     Prozessroute_array_raw,
                     Prozessdetails_raw,
                     Materialinfos_raw,
                     Oekonomische_Parameter_raw,
                     Mitarbeiter_und_Logistik_raw,
                     Gebaeude_raw,
                     GWh_Jahr_Ah_Zelle_raw,
                     rueckgewinnung_raw
                     ):
   
    #print(Prozessroute_array_raw)
    #____________________________________
    #Allgemeine Funktionen
    
    #Sucht das DF zu einem Prozessschritt raus
    def read_prozessInfo(Prozess):
        df = Prozessdetails.loc[Prozessdetails["Prozess"] == Prozess]
        return df
    
    def read_materialinfo(Material):
        df = Materialinfos.loc[Materialinfos["Material"] == Material]
        return df
    
    #____________________________________
    #parsen der Eingangsparameter in pandas df
    Zellergebnisse = pd.DataFrame.from_records(json.loads(Zellergebnisse_raw))
    Zellergebnisse = Zellergebnisse.set_index('Beschreibung')
    
    Zellchemie = pd.DataFrame.from_records(json.loads(Zellchemie_raw)) 
    Zellchemie = Zellchemie.set_index('Beschreibung')
        
    
    b_json = json.loads(Materialinfos_raw)
    complete_df = []
    for Material_tabelle in b_json:
        Material = list(Material_tabelle.keys())[0]
        for Spalte in Material_tabelle[Material]:
            Spalte["Material"]=Material
            complete_df.append(Spalte)
    Materialinfos = pd.DataFrame.from_records(complete_df)
    Materialinfos = Materialinfos.set_index('Beschreibung')
        
    b_json = json.loads(Prozessdetails_raw)
    complete_df = []
    for Prozess_tabelle in b_json:
        Prozess = list(Prozess_tabelle.keys())[0]
        for Spalte in Prozess_tabelle[Prozess]:
            Spalte["Prozess"]=Prozess
            complete_df.append(Spalte)
    Prozessdetails = pd.DataFrame.from_records(complete_df)
    Prozessdetails = Prozessdetails.set_index('Beschreibung')
    
    Oekonomische_Parameter = pd.DataFrame.from_records(json.loads(Oekonomische_Parameter_raw))
    Oekonomische_Parameter = Oekonomische_Parameter.set_index('Beschreibung')
    
    Mitarbeiter_und_Logistik = pd.DataFrame.from_records(json.loads(Mitarbeiter_und_Logistik_raw))
    Mitarbeiter_und_Logistik = Mitarbeiter_und_Logistik.set_index('Beschreibung')
    
    Gebaeude = pd.DataFrame.from_records(json.loads(Gebaeude_raw))
    Gebaeude = Gebaeude.set_index('Beschreibung')

    rueckgewinnung = pd.DataFrame.from_records(json.loads(rueckgewinnung_raw))
    rueckgewinnung = rueckgewinnung.set_index('Beschreibung')

    #____________________________________
    #Kostenrechnung
    
    #leeres DataFrame, wird später gefüllt
    df = pd.DataFrame()
    
    #Anfangsdictionary das dem letzten Schritt übergeben wird, zusätzlich stellt es den Index der Tabelle dar
    # Anfangsmengenwerte errechnen aus dem Zelläquivalent: "wie viel Anodenbeschichtung braucht man für eine Zelle
    
    # Anodenbeschichtung NOCH ÜBERARBEITEN
    Anodenbeschichtung_menge = Zellergebnisse["Wert"]["Cells per year"]*Zellergebnisse["Wert"]["Weight of the anode coating"]/1000 #[kg]
    
    # Kathodenbeschichtung
    Kathodenbeschichtung_menge = Zellergebnisse["Wert"]["Cells per year"]*Zellergebnisse["Wert"]["Weight of the cathode coating"]/1000 #[kg]
    
    #Anodenkollektor
    Anodenkollektor = Zellchemie.loc[Zellchemie['Kategorie'] == "Collector foil anode"].index.tolist()[0] #Raussuchen, welcher Anodenkollektor verwendet wurde
    Anodenkollektor_menge = Zellergebnisse["Wert"]["Cells per year"]*Zellergebnisse["Wert"]["Number of repeating units"]/Zellergebnisse["Wert"]["Sheets/meter anode"] #[m]

    #Kathodenkollektor
    Kathodenkollektor = Zellchemie.loc[Zellchemie['Kategorie'] == "Collector foil cathode"].index.tolist()[0] #Raussuchen, welcher Kathodenkollektor verwendet wurde
    Kathodenkollektor_menge = Zellergebnisse["Wert"]["Cells per year"]*Zellergebnisse["Wert"]["Number of repeating units"]/Zellergebnisse["Wert"]["Sheets/meter cathode"] #[m]
    
    # Separator NOCH ÜBERARBEITEN
    Separator = Zellchemie.loc[Zellchemie['Kategorie'] == "Separator"].index.tolist()[0] #Raussuchen, welcher Separator verwendet wurde
    Separator_menge = Zellergebnisse["Wert"]["Cells per year"]*Zellergebnisse["Wert"]["Total area of separator"]/1e6 #[m²]
    
    #Elektrolyt
    Elektrolyt = Zellchemie.loc[Zellchemie['Kategorie'] == "Electrolyte"].index.tolist()[0] #Raussuchen, welches Elektrolyt verwendet wurde
    Elektrolyt_menge = Zellergebnisse["Wert"]["Cells per year"]*Zellergebnisse["Wert"]["Weight of the electrolyte"]/read_materialinfo(Elektrolyt)["Wert"]["Density"]/1000 #[l]
    
    #Hülle
    Huelle = Zellchemie.loc[Zellchemie['Kategorie'] == "Case"].index.tolist()[0] #Raussuchen, welches Elektrolyt verwendet wurde
    Huelle_menge = Zellergebnisse["Wert"]["Cells per year"] #[-]

    
    schritt_dictionary={
         "Cell equivalent":Zellergebnisse["Wert"]["Cells per year"],
         "Anode coating":Anodenbeschichtung_menge,
         "Cathode coating":Kathodenbeschichtung_menge,
         "Anode collector": Anodenkollektor_menge,
         "Cathode collector": Kathodenkollektor_menge,
         "Separator":Separator_menge,
         "Case":Huelle_menge,
         "Electrolyte":Elektrolyt_menge,
         "Anode coating recovery":0,
         "Cathode coating recovery":0,
         "Anode collector recovery": 0,
         "Cathode collector recovery": 0,
         "Separator recovery":0,
         "Case recovery":0,
         "Electrolyte recovery":0,
         "Number of machines":"",
         "Neue Materialien":"",
         "Space requirements normal room":"",
         "Space requirements for dry room":"",
         "Space requirement laboratory":"",
         "Skilled workers":"",
         "Assistants":"",
         "Energy demand":"",
         'Material costs':"",
         'Personal costs':"",
         'Energy costs':"",
         'Maintenance costs':"",
         'Area costs':"",
         'Imputed interest':"",
         'Economic depreciation':"",
         'Investment':"",
         'Operating days': Mitarbeiter_und_Logistik["Wert"]["Operating days"],
         'Space': 1- (Gebaeude["Wert"]["Factor machine space"] + Gebaeude["Wert"]["Factor intermediate storage areas"] + Gebaeude["Wert"]["Factor additional areas"])/100
         }
    
    #Gleiches Dictionary wie zuvor, mit den entsprechenden Einheiten 
    schritt_dictionary_einheiten={
         "Cell equivalent":"-",
         "Anode coating":"kg",
         "Cathode coating":"kg",
         "Anode collector":"m",
         "Cathode collector":"m",
         "Separator":"m²",
         "Case":"-",
         "Electrolyte":"l",
         "Anode coating recovery":"kg",
         "Cathode coating recovery":"kg",
         "Anode collector recovery":"m",
         "Cathode collector recovery":"m",
         "Separator recovery":"m²",
         "Case recovery":"m²",
         "Electrolyte recovery":"l",
         "Number of machines":"-",
         "Neue Materialien":"-",
         "Space requirements normal room":"m²",
         "Space requirements for dry room":"m²",
         "Space requirement laboratory":"m²",
         "Skilled workers":"-",
         "Assistants":"-",
         "Energy demand":"kWh",
         'Material costs': '$', 
         'Personal costs': '$', 
         'Energy costs': '$', 
         'Maintenance costs': '$', 
         'Area costs': '$', 
         'Imputed interest': '$', 
         'Economic depreciation': '$', 
         'Investment': '$',
         'Operating days': 'days',
         'Space':"-"
         }
    
    #erste Spalte (index) in das df einfügen 
    df["index"] = schritt_dictionary.keys()
    
    #erste Spalte zum Index umformen
    df = df.set_index('index')
    

        #########
 
    #______________________________________


    #____________________________________
    #Materialrückgewinnung
    #Zelle: Das Material, welches am Ende in der Zelle landet
    #Gesamt: Das die Menge des Materials, die zum Prozess zugeeführt wird 
    rueckgewinnung_dict_temp = [{"Material":"Anode coating","Zelle":Anodenbeschichtung_menge,"Gesamt":""},
                           {"Material":"Cathode coating","Zelle":Kathodenbeschichtung_menge,"Gesamt":""},
                           {"Material":"Anode collector","Zelle":Anodenkollektor_menge,"Gesamt":""},
                           {"Material":"Cathode collector","Zelle":Kathodenkollektor_menge,"Gesamt":""},
                           {"Material":"Separator","Zelle":Separator_menge,"Gesamt":""},
                           {"Material":"Electrolyte","Zelle":Elektrolyt_menge,"Gesamt":""},
                           {"Material":"Case","Zelle":Huelle_menge,"Gesamt":""},
                           ]
    rueckgewinnung_dict = []
    
    
    #____________________________________
    #Retrograde Materialflusskalkulation
    Betriebstage = Mitarbeiter_und_Logistik["Wert"]["Operating days"]
    ArbeitStundeproSchicht = Mitarbeiter_und_Logistik["Wert"]["Working hours per shift"]
    SchichtproTag = Mitarbeiter_und_Logistik["Wert"]["Shifts per day"]
    for schritt in reversed(Prozessroute_array_raw):        #Prozessschritte in umgekehrter Reihenfolge durchgehen
        Prozess_name = schritt                          #Kopie des Schritts zur Umwandlung in Funktionsname, ersetzen aller Sonderzeichen durch "_"
        Prozess_name = Prozess_name.replace(' ','_').replace('-','_').replace('/','_')    
        #Übergebene Parameter and die Funtionen zu jedem Schritt: read_prozessInfo(schritt):  , 
        schritt_dictionary = getattr(Prozessfunktionen, Prozess_name)(read_prozessInfo(schritt), #df mit den Infos zum Prozesschritt
                                                                      Zellergebnisse, #Zellergebnisse: Ergebnisse der Zellberechnung
                                                                      Zellchemie, #die Zellchemie
                                                                      Materialinfos, #Infos zu den Materialien
                                                                      schritt_dictionary, #schritt_dictionary: die Parameter die zwischen den Schritten übergeben werden
                                                                      rueckgewinnung #dictionary zu den Anteilen die zurück gewonnen werden können
                                                                      )  

        #die Informationen jedes Prozessschrittes in das df einfügen
        df[schritt] = df.index.to_series().map(schritt_dictionary)
       
    #____________________________________
    #Abschluss Retrograde Materialflusskalkulation
     
           #____________________________________
    #Berechnung der jährlichen Flächenkosten/m², der Investkosten für den Bau und der Flächen 

    flaeche_normalraum = sum(list(df.loc["Space requirements normal room"]))
    flaeche_trockenraum = sum(list(df.loc["Space requirements for dry room"]))
    flaeche_labor = sum(list(df.loc["Space requirement laboratory"]))

    flaechenergebnisse = flaechenberechnung(flaeche_normalraum, flaeche_trockenraum, Gebaeude, Oekonomische_Parameter,flaeche_labor)
    grundstueckskosten = flaechenergebnisse[0]
    flaechenverteilung = flaechenergebnisse[1]
    flaechenkosten_jaehrlich = flaechenergebnisse[2]
    fabrikflaeche = flaechenergebnisse[3]
    Fabrikflaeche_ohne_Produktion = flaechenergebnisse[4]  
   

    #____________________________________
    #Anterograde Wertstromkalkulation  
    #Bestimmen der Einzelkosten
    
    #Betriebstage = 360
    

    Materialkosten = {
        "Anode coating_kosten":Zellergebnisse["Wert"]["Cost per kilogram anode coating"], #[€/kg]
        "Cathode coating_kosten":Zellergebnisse["Wert"]["Cost per kilogram cathode coating"], #[€/kg]
        "Anode collector_kosten":read_materialinfo(Anodenkollektor)["Wert"]["Price"]*read_materialinfo(Anodenkollektor)["Wert"]["Width"]/1000, #[€/m]
        "Cathode collector_kosten":read_materialinfo(Kathodenkollektor)["Wert"]["Price"]*read_materialinfo(Kathodenkollektor)["Wert"]["Width"]/1000, #[€/m]
        "Separator_kosten":read_materialinfo(Separator)["Wert"]["Price"], #[€/m²]
        "Electrolyte_kosten":read_materialinfo(Elektrolyt)["Wert"]["Price"], #[€/kg]
        "Case_kosten":read_materialinfo(Huelle)["Wert"]["Price"], #[€/m²]
        }
    
    Strompreis = Oekonomische_Parameter["Wert"]["Energy cost"] #[€/kWh]
    Stundensatz_hilfskraft = Mitarbeiter_und_Logistik["Wert"]["Hourly rate supporting staff"] #[€/h]
    Stundensatz_facharbeiter = Mitarbeiter_und_Logistik["Wert"]["Hourly rate specialists"] #[€/h]
    Instandhaltungskostensatz = Oekonomische_Parameter["Wert"]["Maintenance rate"] #[%]
    Flächenkosten_Produktionshalle = flaechenkosten_jaehrlich #[€/m²] dauerhafte Kosten pro Jahr?
    Flächenkosten_Trockenraum = flaechenkosten_jaehrlich  #[€/m²] dauerhafte Kosten pro Jahr?
    Stromverbrauch_Trockenraum_Flächennormiert = Gebaeude["Wert"]["Energy consumption dry room, normalized by area"]  #[€/m²] dauerhafte Kosten pro Jahr?
    Zinssatz_Kapitalmarkt = Oekonomische_Parameter["Wert"]["Capital cost"]/100 #[%]
    Nutzungsdauer = Oekonomische_Parameter["Wert"]["Technical service life"] #[%]
    
    Materialkosten_dict = {}
    for schritt in Prozessroute_array_raw:
        
        #Materialkosten
        if df[schritt]["Neue Materialien"]!="":
            liste = df[schritt]["Neue Materialien"].split(";")
            kosten = 0
            for material in liste:
                print(material)
                print(df[schritt][material])

                cost = df[schritt][material]*Materialkosten[material+"_kosten"] 

                kosten += df[schritt][material]*Materialkosten[material+"_kosten"] 

                Materialkosten_dict.update({material:round(cost,2)})
                
                for rueck_material in rueckgewinnung_dict_temp:
                    if material == rueck_material["Material"]:
                        rueck_material["Gesamt"]=df[schritt][material]
                        rueckgewinnung_dict.append(rueck_material)
                        
            df[schritt]["Material costs"]=kosten
        else:
            df[schritt]["Material costs"]=0
            
        #Energiekosten
        df[schritt]["Energy costs"] = df[schritt]["Energy demand"]*Strompreis+df[schritt]["Space requirements for dry room"]*Stromverbrauch_Trockenraum_Flächennormiert*Betriebstage*Strompreis+df[schritt]["Space requirement laboratory"]*Betriebstage*Gebaeude["Wert"]["Energy consumption laboratory, normalized by area"]*Strompreis

        #Personalkosten
        df[schritt]["Personal costs"] = (df[schritt]["Skilled workers"]*Stundensatz_facharbeiter + df[schritt]["Assistants"]*Stundensatz_hilfskraft)*Betriebstage*ArbeitStundeproSchicht*SchichtproTag

        #Instandhaltungskosten
        df[schritt]["Maintenance costs"] = df[schritt]["Investment"]*(Instandhaltungskostensatz/100)
        
        #Flächenkosten
        df[schritt]["Area costs"] = df[schritt]["Space requirements normal room"]*Flächenkosten_Produktionshalle+df[schritt]["Space requirements for dry room"]*Flächenkosten_Trockenraum+df[schritt]["Space requirement laboratory"]*flaechenkosten_jaehrlich
    
        #Kalkulatorische Zinsen
        df[schritt]["Imputed interest"]=df[schritt]["Investment"]*Oekonomische_Parameter["Wert"]["Replacement factor"]*Zinssatz_Kapitalmarkt/100/0.5
        
        #Ökonomische Abschreibung
        df[schritt]["Economic depreciation"]=df[schritt]["Investment"]/Nutzungsdauer
    #Abschluss Anterograde Wertstromkalkulation   
    
    
    #OVERHEAD KOSTEN
    #____________________________________
    #Flächenkalkulation  
   


    #Abschluss Flächenkalkulation

    
    Personalkosten_overhead = sum([sum(list(df.loc[x])) for x in ["Skilled workers","Assistants"]])*ArbeitStundeproSchicht*SchichtproTag*Betriebstage*(
        Mitarbeiter_und_Logistik["Wert"]["Hourly rate indirect staff"]*1/Mitarbeiter_und_Logistik["Wert"]["Lead span"]+
        Mitarbeiter_und_Logistik["Wert"]["Hourly rate cleaning staff"]*1/Mitarbeiter_und_Logistik["Wert"]["Span cleaning staff"])

    Klimatisierung_overhead = fabrikflaeche*Gebaeude["Wert"]["Basic media supply"]*Oekonomische_Parameter["Wert"]["Energy cost"]/1000

    Flaechenkosten_overhead = Fabrikflaeche_ohne_Produktion*flaechenkosten_jaehrlich
        
    fix_cost = Personalkosten_overhead + Klimatisierung_overhead + sum(list(df.loc["Maintenance costs"])) #Overhead Kosten

    overhead_kosten = [
        {
            "group": "Personalkosten",
            "value": Personalkosten_overhead
        },
        {
            "group": "Flächenkosten",
            "value": Flaechenkosten_overhead
        },
        {
            "group": "Klimatisierung",
            "value": Klimatisierung_overhead
        }
    ]
    
    
    
    #____________________________________
    #Overhead Personal
    
    #Abschluss Overhead Personal   
        
        
        
    #____________________________________
    #Klimatisierung
    
    #Abschluss Klimatisierung 
                
        
        
    #____________________________________
    #Steuer
    
    #Abschluss Steuer
                        
        
        
    #____________________________________
    #Investitions-Overhead
    
    #Abschluss Investitions-Overhead
                        
        
        
    #____________________________________
    #Entsorgung
    
    #Abschluss Entsorgung    
                        
        
        
    #____________________________________
    #ORamp up
    
    #Abschluss Ramp up    
     
    Materialkosten_mit_rueckgewinnung = {}
    for Material in Materialkosten_dict:
        Materialkosten_mit_rueckgewinnung[Material]=Materialkosten_dict[Material]-sum(list(df.loc[Material+" recovery"]))*Materialkosten[Material+"_kosten"]



    #____________________________________
    #Levelized costs

    levelized_cost_result = levelized_cost(
        construction_cost_factory = sum(anteil["value"] for anteil in grundstueckskosten),
        lifetime_factory = Gebaeude["Wert"]["Service life"],
        interest_rate = Oekonomische_Parameter["Wert"]["Capital cost"]/100,
        tax_rate = Oekonomische_Parameter["Wert"]["Value added tax"]/100,
        #variable_cost = sum([sum(list(df.loc[x])) for x in ["Materialkosten",
        #                                                "Personalkosten",
        #                                                "Energiekosten",
                                                        #"Instandhaltungskosten",
                                                        #"Flächenkosten",
                                                        #"Kalkulatorische Zinsen",
                                                        #"Ökonomische Abschreibung"
        #                                                ]]),
        Materialkosten = sum(list(df.loc["Material costs"])),
        Materialkosten_mit_rueckgewinnung = sum(Materialkosten_mit_rueckgewinnung.values()),
        Personalkosten = sum(list(df.loc["Personal costs"])),
        Energiekosten = sum(list(df.loc["Energy costs"])),
        fix_cost = fix_cost,
        output_kWh = float(GWh_Jahr_Ah_Zelle_raw["GWh_pro_jahr"])*1000000,
        machine_invest = sum(list(df.loc["Investment"])),
        factory_depreciation = Oekonomische_Parameter["Wert"]["Depreciation period of buildings"],
        machine_depreciation = Oekonomische_Parameter["Wert"]["Technical service life"],
        ramp_up_material = Oekonomische_Parameter["Wert"]["Ramp-up cost material"],
        ramp_up_personal_overhead = Oekonomische_Parameter["Wert"]["Ramp-up costs employees and overhead"]
    )

    
    levelized_cost_aufgeteilt = levelized_cost_result[1]
    levelized_cost_result = levelized_cost_result[0]

    
    
    
    #____________________________________
    #Umformen des df

  
    
    #Einheiten einfügen
    df["UNIT"] = df.index.to_series().map(schritt_dictionary_einheiten)
    #Index wieder als Spalte einfügen
    df['index'] = df.index.tolist()
    #Zeile "neue Materialien" entfernen, ist in der Anzeige irrelevant/ irreführend
    df = df.drop("Neue Materialien",axis=0)
    #Reihenfolge im df drehen
    df = df.iloc[:, ::-1] 


    levelized_cost_aufgeteilt_rueckgewinnung = copy.deepcopy(levelized_cost_aufgeteilt)
    levelized_cost_aufgeteilt_rueckgewinnung[0]["value"] = sum(Materialkosten_mit_rueckgewinnung.values())

    return(df,Materialkosten_dict, rueckgewinnung_dict, grundstueckskosten, flaechenverteilung, levelized_cost_result, overhead_kosten,Materialkosten_mit_rueckgewinnung,levelized_cost_aufgeteilt,levelized_cost_aufgeteilt_rueckgewinnung)
#Kostenberechnung()