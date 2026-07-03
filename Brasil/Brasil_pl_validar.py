def Brasil_QueryValplacas(placas):
    query = """
    REINDEX TABLE """ + placas + """;
    ANALYZE """ + placas + """;
    
    ALTER TABLE """ + placas + """ DROP COLUMN IF EXISTS incidencia;    
    ALTER TABLE """ + placas + """ ADD COLUMN IF NOT EXISTS incidencia varchar;
    ALTER TABLE """ + placas + """ ADD COLUMN IF NOT EXISTS coord_ini varchar;
    ALTER TABLE """ + placas + """ ADD COLUMN IF NOT EXISTS observ_pos varchar;

    ALTER TABLE """ + placas + """ ADD COLUMN IF NOT EXISTS atipico varchar;
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX REEMPLAZAR SIMBOLOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/ 
    UPDATE """ + placas + """ SET nom_estado = regexp_replace(nom_estado, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_estado ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + placas + """ SET nom_mun = regexp_replace(nom_mun, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_mun ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + placas + """ SET nom_distri = regexp_replace(nom_distri, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_distri ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';

    UPDATE """ + placas + """ SET nom_bar = regexp_replace(nom_bar, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_bar ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';

    UPDATE """ + placas + """ SET tipovia = regexp_replace(tipovia, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE tipovia ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + placas + """ SET nomvia = regexp_replace(nomvia, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nomvia ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]'
    AND nomvia != 'S/N';  

    UPDATE """ + placas + """ SET direccion = regexp_replace(direccion, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE direccion ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]'
    AND direccion != 'S/N'; 
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR ESPACIOS INICIO-FIN XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + placas + """ SET nom_estado = TRIM(nom_estado) WHERE nom_estado <> TRIM(nom_estado);
    UPDATE """ + placas + """ SET nom_mun = TRIM(nom_mun) WHERE nom_mun <> TRIM(nom_mun);
    UPDATE """ + placas + """ SET nom_distri = TRIM(nom_distri) WHERE nom_distri <> TRIM(nom_distri);
    UPDATE """ + placas + """ SET nom_bar = TRIM(nom_bar) WHERE nom_bar <> TRIM(nom_bar);
    UPDATE """ + placas + """ SET tipovia = TRIM(tipovia) WHERE tipovia <> TRIM(tipovia);
    UPDATE """ + placas + """ SET nomvia = TRIM(nomvia) WHERE nomvia <> TRIM(nomvia);
    UPDATE """ + placas + """ SET direccion = TRIM(direccion) WHERE direccion <> TRIM(direccion);

    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR DOBLES ESPACIOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + placas + """ SET nom_estado = REPLACE(nom_estado,'  ',' ') WHERE nom_estado LIKE '%  %';
    UPDATE """ + placas + """ SET nom_mun = REPLACE(nom_mun,'  ',' ') WHERE nom_mun LIKE '%  %';
    UPDATE """ + placas + """ SET nom_distri = REPLACE(nom_distri,'  ',' ') WHERE nom_distri LIKE '%  %';
    UPDATE """ + placas + """ SET nom_bar = REPLACE(nom_bar,'  ',' ') WHERE nom_bar LIKE '%  %';
    UPDATE """ + placas + """ SET tipovia = REPLACE(tipovia,'  ',' ') WHERE tipovia LIKE '%  %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'  ',' ') WHERE nomvia LIKE '%  %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'  ',' ') WHERE direccion LIKE '%  %';
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX PASAR A MAYUSCULAS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + placas + """ SET nom_estado = UPPER(nom_estado) WHERE nom_estado <> UPPER(nom_estado);
    UPDATE """ + placas + """ SET nom_mun = UPPER(nom_mun) WHERE nom_mun <> UPPER(nom_mun);
    UPDATE """ + placas + """ SET nom_distri = UPPER(nom_distri) WHERE nom_distri <> UPPER(nom_distri);
    UPDATE """ + placas + """ SET nom_bar = UPPER(nom_bar) WHERE nom_bar <> UPPER(nom_bar);
    UPDATE """ + placas + """ SET tipovia = UPPER(tipovia) WHERE tipovia <> UPPER(tipovia);
    UPDATE """ + placas + """ SET nomvia = UPPER(nomvia) WHERE nomvia <> UPPER(nomvia);
    UPDATE """ + placas + """ SET direccion = UPPER(direccion) WHERE direccion <> UPPER(direccion);    

    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX TODOS LOS NUMEROS VAN SEPARADOS DE LAS LETRASXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + placas + """ SET nomvia = regexp_replace(nomvia,'([A-Za-z])([0-9])','\\1 \\2','g')
    WHERE nomvia ~ '([A-Za-z][0-9])';

    UPDATE """ + placas + """ SET nomvia = regexp_replace(nomvia,'([0-9])([A-Za-z])','\\1 \\2','g')
    WHERE nomvia ~ '([0-9][A-Za-z])';

    UPDATE """ + placas + """ SET direccion = regexp_replace(direccion,'([A-Za-z])([0-9])','\\1 \\2','g')
    WHERE direccion ~ '([A-Za-z][0-9])';

    UPDATE """ + placas + """ SET direccion = regexp_replace(direccion,'([0-9])([A-Za-z])','\\1 \\2','g')
    WHERE direccion ~ '([0-9][A-Za-z])';
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXNUMERO ESPACIO LETRA ESPACIO LETRA SE DEBEN UNIRXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    
    UPDATE """ + placas + """ SET nomvia = regexp_replace(nomvia,'([0-9]) ([A-Za-z]) ([A-Za-z])\\b','\\1 \\2\\3','g')
    WHERE nomvia ~ '([0-9]) ([A-Za-z]) ([A-Za-z])\\b';    
    
    UPDATE """ + placas + """ SET direccion = regexp_replace(direccion,'([0-9]) ([A-Za-z]) ([A-Za-z])\\b','\\1 \\2\\3','g')
    WHERE direccion ~ '([0-9]) ([A-Za-z]) ([A-Za-z])\\b';    

    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX VALIDAR incidencia XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    
    DROP TABLE IF EXISTS tabla_temporal;
    """
    #print(query)
    return query
    
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import MultiPoint, Point, LineString, MultiLineString
from shapely.ops import linemerge
from rtree import index as indexx
import re
import networkx as nx
import math

def Brasil_pl_incidencia(mv_brasil, placas_brasil, texto_filtro, key, idx):

    mifiltro=texto_filtro #####AQUI VA EL FILTRO#####
    partes = mifiltro.split(',')
    dep=partes[0]
    prov=partes[1]

    placas_brasil['incidencia'] = None

    if key ==1:

        # 1. Validar registro con caracteres
        id_excp = list(placas_brasil.loc[placas_brasil['exclusion'].str.contains(r'\[1\]', na=False),'id'])
        # Expresión regular para caracteres especiales
        simbolos = r'[|!"#@$%&/()¿¡¨{}\[\]._:,;+\-*=/¬°]'

        # Función para marcar la inconsistencia si hay caracteres especiales en alguna columna específica
        def marcar_simbolos(row):
            if row['nomvia'] != 'S/N':
                columnas = ['nom_estado', 'nom_mun', 'nom_distri', 'nom_bar', 'tipovia', 'nomvia', 'direccion']
                for col in columnas:
                    if pd.notna(row[col]) and re.search(simbolos, row[col]) and (row['id'] not in id_excp):
                        return '1. Validar registro con caracteres - '
            return None

        # Aplicar la función para marcar incidencia
        placas_brasil['incidencia'] = placas_brasil.apply(marcar_simbolos, axis=1)   
    
    if key ==2:    
    
        #2 PLACAS ID_CAPA REPETIDO
        frecuencias = placas_brasil['id_capa'].value_counts().reset_index()
        valor_dict = frecuencias[frecuencias['count'] > 1].set_index('id_capa')['count'].to_dict()
        id_excp = list(placas_brasil.loc[placas_brasil['exclusion'].str.contains(r'\[2\]', na=False),'id'])
        placas_brasil['incidencia'] = placas_brasil.apply(
            lambda row: f"{row['incidencia']} - 2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['incidencia'] is not None and row['id_capa'] in valor_dict and row['id'] not in id_excp else 
            f"2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['incidencia'] is  None and row['id_capa'] in valor_dict and row['id'] not in id_excp else
            row['incidencia'],
            axis=1
        )

    if key ==3:
        
        #3 PLACAS PREFIJO
        
        id_excp = list(placas_brasil.loc[placas_brasil['exclusion'].str.contains(r'\[3\]', na=False),'id']) 
                
        filtro = placas_brasil[(placas_brasil['cod_estado']==dep) & (placas_brasil['cod_mun']==prov) & (placas_brasil['tipovia'].isna())]
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=1))
            resultados.append([row.Index,candidates[0]])
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno'])
        tiponulo=[]
        #-------------------
        for row in resultados_df.itertuples(index=False):
            if placas_brasil.at[row[0],'id'] in id_excp:
                continue
            if not (mv_brasil.at[row[1], 'tipovia']==None):
                tiponulo.append(row[0])
           
        cond1 = placas_brasil.index.isin(tiponulo)
        cond2 = placas_brasil['incidencia'].isna()
        cond3 = placas_brasil['exclusion'].str.contains(r'\[3\]', na=False)
        placas_brasil.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_brasil['incidencia'] + " - 3. Tipovia vacio"
        placas_brasil.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "3. Tipovia vacio"  
        
    if key ==4:
    
        #4 VIA VACIA
        id_excp = list(placas_brasil.loc[placas_brasil['exclusion'].str.contains(r'\[4\]', na=False),'id']) 
                
        filtro = placas_brasil[(placas_brasil['cod_estado']==dep) & (placas_brasil['cod_mun']==prov) & (placas_brasil['nomvia'].isna())]
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=1))
            resultados.append([row.Index,candidates[0]])
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno'])
        nomnulo=[]
        #-------------------
        for row in resultados_df.itertuples(index=False):
            if placas_brasil.at[row[0],'id'] in id_excp:
                continue
            if not (mv_brasil.at[row[1], 'nomvia']==None):
                nomnulo.append(row[0])
                
        cond1 = placas_brasil.index.isin(nomnulo)
        cond2 = placas_brasil['incidencia'].isna()
        cond3 = placas_brasil['exclusion'].str.contains(r'\[4\]', na=False)
        placas_brasil.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_brasil['incidencia'] + " - 4. nombre via vacio"
        placas_brasil.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "4. Nombre via vacio" 

    if key ==5:

        #5 generadora VACIA
        
        id_excp = list(placas_brasil.loc[placas_brasil['exclusion'].str.contains(r'\[5\]', na=False),'id'])
                
        filtro = placas_brasil[(placas_brasil['cod_estado']==dep) & (placas_brasil['cod_mun']==prov) & (placas_brasil['generadora'].isna())]
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=1))
            resultados.append([row.Index,candidates[0]])
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno'])
        gennula=[]
        #-------------------
        for row in resultados_df.itertuples(index=False):
            if placas_brasil.at[row[0],'id'] in id_excp:
                continue
            if not (mv_brasil.at[row[1], 'generadora']==None):
                gennula.append(row[0])
                
        cond1 = placas_brasil.index.isin(gennula)
        cond2 = placas_brasil['incidencia'].isna()
        cond3 = placas_brasil['exclusion'].str.contains(r'\[5\]', na=False)
        placas_brasil.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_brasil['incidencia'] + " - 5. Generadora vacia"
        placas_brasil.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "5. Generadora vacia"  
    
    if key ==6:  

        id_excp = list(placas_brasil.loc[placas_brasil['exclusion'].str.contains(r'\[6\]', na=False),'id'])
        #6 PLACAS VS MAVVIAL

        filtro = placas_brasil[(placas_brasil['cod_estado']==dep) & (placas_brasil['cod_mun']==prov)]
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=2))
            resultados.append([row.Index,candidates[0],candidates[1]])
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno','mv_dos'])
        copia_malla = mv_brasil.copy()
        copia_malla['list_generadora']=copia_malla['generadora'].apply(lambda x: [''] if x is None else x.split('|'))
        #-------------------
        for row in resultados_df.itertuples(index=False):
            if placas_brasil.at[row[0],'id'] in id_excp:
                continue
            if not ((placas_brasil.at[row[0], 'nomvtotal']==copia_malla.at[row[1], 'nomvtotal']) and (placas_brasil.at[row[0], 'generadora'] in copia_malla.at[row[1], 'list_generadora'])):
                if not ((placas_brasil.at[row[0], 'nomvtotal']==copia_malla.at[row[2], 'nomvtotal']) and (placas_brasil.at[row[0], 'generadora'] in copia_malla.at[row[2], 'list_generadora'])):
                    if placas_brasil.at[row[0], 'incidencia'] is None:
                        placas_brasil.at[row[0], 'incidencia']='6. No corresponde la placa con el nombre de via'
                    else:
                        placas_brasil.at[row[0], 'incidencia']=placas_brasil.at[row[0], 'incidencia'] + ' - 6. No corresponde direccion con el de la via'
    
    if key ==7:   

        # 7 NUM PUERTA REPETIDO
        agrupados = placas_brasil[(placas_brasil['cod_estado']==dep) & (placas_brasil['cod_mun']==prov)][['cod_distri','nomvtotal','generadora']].dropna().drop_duplicates().reset_index(drop=True)

        copia_placas=placas_brasil[(placas_brasil['cod_estado']==dep) & (placas_brasil['cod_mun']==prov)].dropna(subset=['cod_estado', 'cod_mun','cod_distri','nomvtotal','generadora']).reset_index(drop=False).drop(['cod_estado', 'cod_mun'], axis=1).set_index(['cod_distri','nomvtotal','generadora']).sort_index()
        print(copia_placas.columns)

        repetidos_total=[]
        errores_total=[]
        saltos_total=[]
        for row in agrupados.itertuples(index=False):
            filtro = copia_placas.loc[(row[0],row[1],row[2])].sort_values(by='placa').set_index('placa')
            indices = filtro.index.tolist()
            ind_repetidos = list(item for item in indices if indices.count(item) > 1)
            repetidos_total.extend(list(filtro.loc[ind_repetidos,'index']))

        #MARCAR ERRORES
        #MARCAR PUERTAS REPETIDAS
        repetidos_total=list(set(repetidos_total))

        cond1 = placas_brasil.index.isin(repetidos_total)
        cond2 = placas_brasil['incidencia'].isna()
        cond3 = placas_brasil['exclusion'].str.contains(r'\[7\]', na=False)
        placas_brasil.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_brasil['incidencia'] + " - 7. Placa repetida"
        placas_brasil.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "7. Placa repetida" 

    if key ==8: 
        
        #8 COSTADO INCORRECTO Y 9 SALTO DE PLACAS >4

        agrupados = placas_brasil[(placas_brasil['cod_estado']==dep) & (placas_brasil['cod_mun']==prov)][['cod_distri','nomvtotal','generadora']].dropna().drop_duplicates().reset_index(drop=True)

        copia_placas = placas_brasil[(placas_brasil['cod_estado']==dep) & (placas_brasil['cod_mun']==prov) & (~placas_brasil['nomvtotal'].str.contains('S/N', na=False)) & (placas_brasil['atipico'].isna())][['cod_distri','nomvtotal','generadora','placa','geom']].dropna().reset_index(drop=False).set_index(['cod_distri','nomvtotal','generadora']).sort_index()
        repetidos_total=[]
        errores_total=[]
        saltos_total=[]
        for row in agrupados.itertuples(index=False):
            filtro = copia_placas.loc[(row[0],row[1],row[2])].sort_values(by='placa').set_index('placa')
            indices = filtro.index.tolist()
            ind_repetidos = list(item for item in indices if indices.count(item) > 1)
            repetidos_total.extend(list(filtro.loc[ind_repetidos,'index']))
            pares = [num for num in indices if int(num) % 2 == 0]
            impares = [num for num in indices if int(num) % 2 != 0]
            if len(pares)>1:
                rep=0
                ciclo = False
                for actual, siguiente in zip(pares, pares[1:]):
                    if actual == siguiente:
                        if rep==0:
                            conteo = (filtro.index == actual).sum()-1
                        linea = LineString([filtro.at[actual,'geom'][rep], filtro.at[siguiente,'geom'][rep+1]])
                        rep+=1
                        ciclo = True
                    else:
                        if ((filtro.index == siguiente).sum()-1)>0:
                            if (int(siguiente)-int(actual))>18:
                                saltos_total.extend(list(filtro.loc[siguiente,'index']))
                            pfinal=filtro.at[siguiente,'geom'][0]
                        else:
                            if (int(siguiente)-int(actual))>18:
                                saltos_total.append(filtro.at[siguiente,'index'])
                            pfinal=filtro.at[siguiente,'geom']
                        if ciclo == True:
                            linea = LineString([filtro.at[actual,'geom'][rep], pfinal])
                            ciclo = False
                            rep=0
                        else:
                            linea = LineString([filtro.at[actual,'geom'], pfinal])
                    candidates = list(idx.intersection(linea.bounds))
                    for i in candidates:
                        if linea.intersects(mv_brasil.geometry[i]):
                            errores_total.extend(list(filtro.loc[[actual,siguiente],'index']))
                            break                
            if len(impares)>1:
                rep=0
                ciclo = False
                for actual, siguiente in zip(impares, impares[1:]):
                    if actual == siguiente:
                        if rep==0:
                            conteo = (filtro.index == actual).sum()-1
                        linea = LineString([filtro.at[actual,'geom'][rep], filtro.at[siguiente,'geom'][rep+1]])
                        rep+=1
                        ciclo = True
                    else:
                        if ((filtro.index == siguiente).sum()-1)>0:
                            if (int(siguiente)-int(actual))>18:
                                saltos_total.extend(list(filtro.loc[siguiente,'index']))
                            pfinal=filtro.at[siguiente,'geom'][0]
                        else:
                            if (int(siguiente)-int(actual))>18:
                                saltos_total.append(filtro.at[siguiente,'index'])
                            pfinal=filtro.at[siguiente,'geom']
                        if ciclo == True:
                            linea = LineString([filtro.at[actual,'geom'][rep], pfinal])
                            ciclo = False
                            rep=0
                        else:
                            linea = LineString([filtro.at[actual,'geom'], pfinal])
                    candidates = list(idx.intersection(linea.bounds))
                    for i in candidates:
                        if linea.intersects(mv_brasil.geometry[i]):
                            errores_total.extend(list(filtro.loc[[actual,siguiente],'index']))
                            break

        #MARCAR ERRORES COSTADOS
        errores_total=list(set(errores_total))
        cond1 = placas_brasil.index.isin(errores_total)
        cond2 = placas_brasil['incidencia'].isna()
        cond3 = placas_brasil['exclusion'].str.contains(r'\[8\]', na=False)
        placas_brasil.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_brasil['incidencia'] + " - 8. Error costados"
        placas_brasil.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "8. Error costados"

        #MARCAR ERRORES SALTOS
        saltos_total=list(set(saltos_total))
        cond1 = placas_brasil.index.isin(saltos_total)
        cond2 = placas_brasil['incidencia'].isna()
        cond3 = placas_brasil['exclusion'].str.contains(r'\[9\]', na=False)
        placas_brasil.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_brasil['incidencia'] + " - 9. Salto de placa"
        placas_brasil.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "9. Salto de placa"
       
    if key == 10:
        def ordenar_placas(filtro_tipo):
            lista = [list(lista) for lista in zip(filtro_tipo['index'], filtro_tipo.index, filtro_tipo['geom'],filtro_tipo['coord_ini'])]
            for i in range(len(lista) - 2):
                dist1 = lista[i][2].distance(lista[i+1][2])
                dist2 = lista[i][2].distance(lista[i+2][2])
                if dist2<dist1:
                    if (lista[i][1] == lista[i+1][1]) | (lista[i+1][1] == lista[i+2][1]):
                        continue
                    dif_p1 = lista[i+1][1]-lista[i][1]
                    dif_p2 = lista[i+2][1]-lista[i][1]
                    comp_p1 = abs(dif_p1-dist1)
                    comp_p2 = abs(dif_p2-dist2)
                    if (comp_p1>comp_p2):
                        if (lista[i+1][1]-lista[i][1])<dist2:
                            if lista [i+1][3] is None:
                                lista [i+1][3]='Movido'
                                coordenadas.append([lista[i+1][0],str(geom_original.loc[lista[i+1][0],'geom'].wkt)])
                            ang = (math.atan2(lista[i+2][2].x-lista[i][2].x,lista[i+2][2].y-lista[i][2].y)+2*math.pi)%(2*math.pi)
                            nmas = (lista[i+1][1]-lista[i][1])*math.cos(ang)
                            emas = (lista[i+1][1]-lista[i][1])*math.sin(ang)
                            lista[i+1][2] = placas_brasil.loc[lista[i+1][0],'geom'] = Point(lista[i][2].x+emas,lista[i][2].y+nmas)
                            edicion.add(lista[i+1][0])
                        else:
                            if lista [i+1][3] is None:
                                lista [i+1][3]='Movido'
                                coordenadas.append([lista[i+1][0],str(geom_original.loc[lista[i+1][0],'geom'].wkt)])
                            if lista [i+2][3] is None:
                                lista [i+2][3]='Movido'
                                coordenadas.append([lista[i+2][0],str(geom_original.loc[lista[i+2][0],'geom'].wkt)])
                            placas_brasil.loc[lista[i+1][0],'geom'] = placas_brasil.loc[lista[i+2][0],'geom']
                            placas_brasil.loc[lista[i+2][0],'geom'] = lista[i+1][2]
                            lista[i+1][2] = placas_brasil.loc[lista[i+1][0],'geom']
                            lista[i+2][2] = placas_brasil.loc[lista[i+2][0],'geom']
                            edicion.add(lista[i+1][0])
                            edicion.add(lista[i+2][0])
                    elif(comp_p2>comp_p1):
                        if (lista[i+2][1]-lista[i][1])>dist1:
                            if lista [i+2][3] is None:
                                lista [i+2][3]='Movido'
                                coordenadas.append([lista[i+2][0],str(geom_original.loc[lista[i+2][0],'geom'].wkt)])
                            ang = (math.atan2(lista[i+1][2].x-lista[i][2].x,lista[i+1][2].y-lista[i][2].y)+2*math.pi)%(2*math.pi)
                            nmas = (lista[i+2][1]-lista[i+1][1])*math.cos(ang)
                            emas = (lista[i+2][1]-lista[i+1][1])*math.sin(ang)
                            lista[i+2][2] = placas_brasil.loc[lista[i+2][0],'geom'] = Point(lista[i+1][2].x+emas,lista[i+1][2].y+nmas)
                            edicion.add(lista[i+2][0])
                        else:
                            if lista [i+1][3] is None:
                                coordenadas.append([lista[i+1][0],str(geom_original.loc[lista[i+1][0],'geom'].wkt)])
                                lista [i+1][3]='Movido'
                            if lista [i+2][3] is None:
                                lista [i+2][3]='Movido'
                                coordenadas.append([lista[i+2][0],str(geom_original.loc[lista[i+2][0],'geom'].wkt)])
                            placas_brasil.loc[lista[i+1][0],'geom'] = placas_brasil.loc[lista[i+2][0],'geom']
                            placas_brasil.loc[lista[i+2][0],'geom'] = lista[i+1][2]
                            lista[i+1][2] = placas_brasil.loc[lista[i+1][0],'geom']
                            lista[i+2][2] = placas_brasil.loc[lista[i+2][0],'geom']
                            edicion.add(lista[i+1][0])
                            edicion.add(lista[i+2][0])
                    else:
                        if lista [i+1][3] is None:
                            coordenadas.append([lista[i+1][0],str(geom_original.loc[lista[i+1][0],'geom'].wkt)])
                            lista [i+1][3]='Movido'
                        if lista [i+2][3] is None:
                            lista [i+2][3]='Movido'
                            coordenadas.append([lista[i+2][0],str(geom_original.loc[lista[i+2][0],'geom'].wkt)])
                        placas_brasil.loc[lista[i+1][0],'geom'] = placas_brasil.loc[lista[i+2][0],'geom']
                        placas_brasil.loc[lista[i+2][0],'geom'] = lista[i+1][2]
                        lista[i+1][2] = placas_brasil.loc[lista[i+1][0],'geom']
                        lista[i+2][2] = placas_brasil.loc[lista[i+2][0],'geom']
                        edicion.add(lista[i+1][0])
                        edicion.add(lista[i+2][0])

        #Hallar agrupados
        geom_original=placas_brasil[['geom']].copy()
        placas_brasil=placas_brasil.to_crs(epsg=3857)
        copia_placas=placas_brasil[(placas_brasil['cod_estado']==dep) & (placas_brasil['cod_mun']==prov) & (placas_brasil['exclusion'].isna())].dropna(subset=['cod_distri','nomvtotal','generadora','placa']).reset_index(drop=False).set_index(['cod_distri','nomvtotal','generadora']).sort_index()[['index','placa','geom','coord_ini']]#.to_crs(epsg=3857)
        copia_placas['placa'] = copia_placas['placa'].astype(int)
        edicion = set()
        coordenadas = []
        agrupados = placas_brasil[(placas_brasil['cod_estado']==dep) & (placas_brasil['cod_mun']==prov) & (~placas_brasil['nomvtotal'].str.contains('S/N', na=False)) ][['cod_distri','nomvtotal','generadora','placa']].dropna().drop('placa', axis=1).drop_duplicates()
        for row in agrupados.itertuples(index=False):
            filtro = copia_placas.loc[(row[0],row[1],row[2])].sort_values(by='placa').set_index('placa')
            indices = filtro.index.tolist()
            pares = filtro[filtro.index % 2 == 0]
            impares = filtro[filtro.index % 2 != 0]
            if len(pares)>2:
                ordenar_placas(pares)
            if len(impares)>2:
                ordenar_placas(impares)
        placas_brasil=placas_brasil.to_crs(epsg=4326)

        #TRAER  COORDENADAS
        df = pd.DataFrame(coordenadas, columns=['idx', 'coorde'])
        merge = placas_brasil.join(df.set_index('idx'))
        merge['coord_ini'] = merge['coord_ini'].fillna(merge['coorde'])
        placas_brasil = merge.drop(columns=['coorde'])

        #MARCAR 
        cond1 = placas_brasil.index.isin(edicion)
        cond2 = placas_brasil['observ_pos'].isna()
        placas_brasil.loc[cond1 & ~cond2, 'observ_pos'] = placas_brasil['observ_pos'] + " - Posición modificada"
        placas_brasil.loc[cond1 & cond2, 'observ_pos'] = "Posición modificada"

        #Marca devolucion
        placas_brasil['edicion10']=None
        placas_brasil.loc[cond1,'edicion10'] = 'SI'
        
    return placas_brasil

def Brasil_validar_placas(engine, mavvial, placas, texto_filtro, seleccionados):

    mifiltro=texto_filtro #####AQUI VA EL FILTRO#####
    partes = mifiltro.split(',')
    dep=partes[0]
    prov=partes[1]

    campos_1 = 'id,geom,nom_estado,nom_mun,nom_distri,nom_bar,tipovia,nomvia,direccion,atipico'
    campos_2 = 'id,geom,id_capa,atipico'
    campos_3 = 'id,geom,cod_estado,cod_mun,tipovia,atipico'
    campos_4 = 'id,geom,cod_estado,cod_mun,nomvia,atipico'
    campos_5 = 'id,geom,cod_estado,cod_mun,generadora,atipico'
    campos_6 = 'id,geom,cod_estado,cod_mun,nomvtotal,generadora,placa,atipico'
    campos_7 = 'id,geom,cod_estado,cod_mun,cod_distri,nomvtotal,generadora,placa,atipico'
    campos_8 = 'id,geom,cod_estado,cod_mun,cod_distri,nomvtotal,generadora,placa,atipico'
    campos_10 = 'id,geom,cod_estado,cod_mun,cod_distri,nomvtotal,generadora,placa,atipico,coord_ini,observ_pos'
    
    campos = {1:campos_1,2:campos_2,3:campos_3,4:campos_4,5:campos_5,6:campos_6,7:campos_7,8:campos_8,10:campos_10}

    # Crear un conjunto para almacenar campos únicos
    columnas_consulta = set()

    # Recorrer los campos seleccionados y agregar los valores al conjunto
    for key in seleccionados:
        if key in campos:
            columnas_consulta.update(campos[key].split(','))  # Dividir por coma y agregar cada campo al conjunto

    # Convertir los campos únicos a una cadena concatenada
    final_fields = ", ".join(sorted(columnas_consulta))  # Ordenar para mayor legibilidad

    # ********* Como Traer la Placas al DataFrame *********

    sql = f"SELECT {final_fields} FROM {placas} WHERE cod_estado = '{dep}' AND cod_mun = '{prov}';"
    placas_brasil = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
    placas_brasil['incidencia'] = None
    placas_brasil['exclusion'] = placas_brasil['atipico'].apply(
        lambda mi_string: ','.join([f"[{x}]" for x in mi_string.replace(" ", "").split(",")]) 
        if mi_string is not None else None
	)
    
    """for key in seleccionados:
        if key in {1, 2, 7}:

            mv_brasil = ''
            placas_brasil = Brasil_pl_incidencia(mv_brasil, placas_brasil, texto_filtro, key)
        
        else:

            #TRAER MALLA
            sql=f"SELECT id, geom, tipovia, nomvia, nomvtotal, generadora FROM {mavvial} WHERE cod_estado = '{dep}' AND cod_mun = '{prov}';"
            mv_brasil = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
                    
            placas_brasil = Brasil_pl_incidencia(mv_brasil, placas_brasil, texto_filtro, key)
       
    #Llevar informacion
    df_temporal = placas_brasil[['id', 'incidencia']]
    df_temporal.to_sql('tabla_temporal', con=engine, index=False, if_exists='replace')"""
    
    if (set(seleccionados) - {1,2,7,10}) != set():#Que no
        #TRAER MALLA
        sql=f"SELECT id, geom, tipovia, nomvia, nomvtotal, generadora FROM {mavvial} WHERE cod_estado = '{dep}' AND cod_mun = '{prov}';"
        mv_brasil = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
        
        if ({3,4,5,6,8} & set(seleccionados)) != set():#Que si
            #AUX PARA CORRER MV
            idx = indexx.Index()
            # Agregar líneas al índice
            for i, geometry in enumerate(mv_brasil.geometry):
                if geometry is not None:
                    idx.insert(i, geometry.bounds)
        else:
            idx=''
                    
    else:
        print('me cai')
        mv_brasil='' 
        idx=''        
    
    for key in seleccionados:
        placas_brasil = Brasil_pl_incidencia(mv_brasil, placas_brasil, texto_filtro, key, idx)
    
    if 10 in seleccionados:
        if set(seleccionados) == {10}:
            df_temporal = placas_brasil[placas_brasil['edicion10'].notna()][['id','observ_pos','coord_ini','geom']]
        else:
            df_temporal = placas_brasil[placas_brasil['edicion10'].notna() | placas_brasil['incidencia'].notna()][['id','incidencia','observ_pos','coord_ini','geom']]
        df_temporal.to_postgis('tabla_temporal', con=engine, index=False, if_exists='replace')
    else:
        df_temporal = placas_brasil[placas_brasil['incidencia'].notna()][['id', 'incidencia']]
        df_temporal.to_sql('tabla_temporal', con=engine, index=False, if_exists='replace')

