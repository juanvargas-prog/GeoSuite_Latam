def Gtm_QueryValplacas(placas):
    query = """
    REINDEX TABLE """ + placas + """;
    ANALYZE """ + placas + """;
    
    ALTER TABLE """ + placas + """ DROP COLUMN IF EXISTS incidencia;    
    ALTER TABLE """ + placas + """ ADD COLUMN IF NOT EXISTS incidencia varchar;
    ALTER TABLE """ + placas + """ ADD COLUMN IF NOT EXISTS coord_ini varchar;
    ALTER TABLE """ + placas + """ ADD COLUMN IF NOT EXISTS obs_qa varchar;
    
    ALTER TABLE """ + placas + """ ADD COLUMN IF NOT EXISTS atipico varchar;
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX REEMPLAZAR SIMBOLOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/  
    UPDATE """ + placas + """ SET nom_dep = regexp_replace(nom_dep, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_dep ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + placas + """ SET nom_mun = regexp_replace(nom_mun, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_mun ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + placas + """ SET nom_zona = regexp_replace(nom_zona, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_zona ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + placas + """ SET nom_urb = regexp_replace(nom_urb, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_urb ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + placas + """ SET tipovia = regexp_replace(tipovia, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE tipovia ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + placas + """ SET nomvia = regexp_replace(nomvia, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nomvia ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]'
    AND nomvia != 'S/N';
    
    UPDATE """ + placas + """ SET direccion = regexp_replace(direccion, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE direccion ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]'
    AND nomvia != 'S/N';
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR ESPACIOS INICIO-FIN XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + placas + """ SET nom_dep = TRIM(nom_dep) WHERE nom_dep <> TRIM(nom_dep);
    UPDATE """ + placas + """ SET nom_mun = TRIM(nom_mun) WHERE nom_mun <> TRIM(nom_mun);
    UPDATE """ + placas + """ SET nom_zona = TRIM(nom_zona) WHERE nom_zona <> TRIM(nom_zona);
    UPDATE """ + placas + """ SET nom_urb = TRIM(nom_urb) WHERE nom_urb <> TRIM(nom_urb);
    UPDATE """ + placas + """ SET tipovia = TRIM(tipovia) WHERE tipovia <> TRIM(tipovia);
    UPDATE """ + placas + """ SET nomvia = TRIM(nomvia) WHERE nomvia <> TRIM(nomvia);
    UPDATE """ + placas + """ SET direccion = TRIM(direccion) WHERE direccion <> TRIM(direccion);

    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR DOBLES ESPACIOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + placas + """ SET nom_dep = REPLACE(nom_dep,'  ',' ') WHERE nom_dep LIKE '%  %';
    UPDATE """ + placas + """ SET nom_mun = REPLACE(nom_mun,'  ',' ') WHERE nom_mun LIKE '%  %';
    UPDATE """ + placas + """ SET nom_zona = REPLACE(nom_zona,'  ',' ') WHERE nom_zona LIKE '%  %';
    UPDATE """ + placas + """ SET nom_urb = REPLACE(nom_urb,'  ',' ') WHERE nom_urb LIKE '%  %';
    UPDATE """ + placas + """ SET tipovia = REPLACE(tipovia,'  ',' ') WHERE tipovia LIKE '%  %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'  ',' ') WHERE nomvia LIKE '%  %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'  ',' ') WHERE direccion LIKE '%  %';
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX PASAR A MAYUSCULAS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + placas + """ SET nom_dep = UPPER(nom_dep) WHERE nom_dep <> UPPER(nom_dep);
    UPDATE """ + placas + """ SET nom_mun = UPPER(nom_mun) WHERE nom_mun <> UPPER(nom_mun);
    UPDATE """ + placas + """ SET nom_zona = UPPER(nom_zona) WHERE nom_zona <> UPPER(nom_zona);
    UPDATE """ + placas + """ SET nom_urb = UPPER(nom_urb) WHERE nom_urb <> UPPER(nom_urb);
    UPDATE """ + placas + """ SET tipovia = UPPER(tipovia) WHERE tipovia <> UPPER(tipovia);
    UPDATE """ + placas + """ SET nomvia = UPPER(nomvia) WHERE nomvia <> UPPER(nomvia);
    UPDATE """ + placas + """ SET direccion = UPPER(direccion) WHERE direccion <> UPPER(direccion);
    
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
import math

def Gtm_pl_incidencia(mv_gtm, placas_gtm, manzanas_gtm, texto_filtro, key,idx):
    
    if key ==1:
        # 1. Validar registro con caracteres
        id_excp = list(placas_gtm.loc[placas_gtm['exclusion'].str.contains(r'\[1\]', na=False),'id'])
        # Expresión regular para caracteres especiales
        simbolos = r'[|!"#@$%&/()¿¡¨{}\[\]._:,;+\-*=/¬°]'

        # Función para marcar la inconsistencia si hay caracteres especiales en alguna columna específica
        def marcar_simbolos(row):
            if row['nomvia'] != 'S/N':
                columnas = ['nom_dep', 'nom_mun', 'nom_zona', 'nom_urb', 'tipovia', 'nomvia', 'direccion']
                for col in columnas:
                    if pd.notna(row[col]) and re.search(simbolos, row[col]) and (row['id'] not in id_excp):
                        return '1. Validar registro con caracteres - '
            return None

        # Aplicar la función para marcar incidencia
        placas_gtm['incidencia'] = placas_gtm.apply(marcar_simbolos, axis=1)   
        
    if key ==2:
        #2 PLACAS ID_CAPA REPETIDO
        frecuencias = placas_gtm['id_capa'].value_counts().reset_index()
        valor_dict = frecuencias[frecuencias['count'] > 1].set_index('id_capa')['count'].to_dict()
        id_excp = list(placas_gtm.loc[placas_gtm['exclusion'].str.contains(r'\[2\]', na=False),'id'])
        placas_gtm['incidencia'] = placas_gtm.apply(
            lambda row: f"{row['incidencia']} - 2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['incidencia'] is not None and row['id_capa'] in valor_dict and row['id'] not in id_excp else 
            f"2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['incidencia'] is  None and row['id_capa'] in valor_dict and row['id'] not in id_excp  else
            row['incidencia'],
            axis=1
        )
        
    if key ==3:
        #3 PLACAS PREFIJO
        id_excp = list(placas_gtm.loc[placas_gtm['exclusion'].str.contains(r'\[3\]', na=False),'id'])
        
        filtro = placas_gtm[(placas_gtm['cod_mun']==texto_filtro) & (placas_gtm['tipovia'].isna())]
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=1))
            resultados.append([row.Index,candidates[0]])
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno'])
        tiponulo=[]
        #-------------------
        for row in resultados_df.itertuples(index=False):
            if placas_gtm.at[row[0],'id'] in id_excp:
                continue
            if not (mv_gtm.at[row[1], 'tipovia']==None):
                tiponulo.append(row[0])
                
        cond1 = placas_gtm.index.isin(tiponulo)
        cond2 = placas_gtm['incidencia'].isna()
        cond3 = placas_gtm['exclusion'].str.contains(r'\[3\]', na=False)
        placas_gtm.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_gtm['incidencia'] + " - 3. Tipovia vacio"
        placas_gtm.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "3. Tipovia vacio"   
    
    if key ==4:
        #4 VIA VACIA
        id_excp = list(placas_gtm.loc[placas_gtm['exclusion'].str.contains(r'\[4\]', na=False),'id'])
                
        filtro = placas_gtm[(placas_gtm['cod_mun']==texto_filtro) & ((placas_gtm['nomvia'].isna()) | (placas_gtm['nomvia'] == 'S/N'))]
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=1))
            resultados.append([row.Index,candidates[0]])
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno'])
        nomnulo=[]
        #-------------------
        for row in resultados_df.itertuples(index=False):
            if placas_gtm.at[row[0],'id'] in id_excp:
                continue
            if mv_gtm.at[row[1], 'nomvia'] is not None and mv_gtm.at[row[1], 'nomvia'] != 'S/N':
                nomnulo.append(row[0])
                
        cond1 = placas_gtm.index.isin(nomnulo)
        cond2 = placas_gtm['incidencia'].isna()
        cond3 = placas_gtm['exclusion'].str.contains(r'\[4\]', na=False)
        placas_gtm.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_gtm['incidencia'] + " - 4. Nomvia vacio"
        placas_gtm.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "4. Nomvia vacio"   
        
        
    if key ==5:
        #5 generadora VACIA
        id_excp = list(placas_gtm.loc[placas_gtm['exclusion'].str.contains(r'\[5\]', na=False),'id'])
                
        filtro = placas_gtm[(placas_gtm['cod_mun']==texto_filtro) & (placas_gtm['generadora'].isna())]
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=1))
            resultados.append([row.Index,candidates[0]])
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno'])
        gennula=[]
        #-------------------
        for row in resultados_df.itertuples(index=False):
            if placas_gtm.at[row[0],'id'] in id_excp:
                continue
            if not (mv_gtm.at[row[1], 'generadora']==None):
                gennula.append(row[0])
                
        cond1 = placas_gtm.index.isin(gennula)
        cond2 = placas_gtm['incidencia'].isna()
        cond3 = placas_gtm['exclusion'].str.contains(r'\[5\]', na=False)
        placas_gtm.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_gtm['incidencia'] + " - 5. Generadora vacia"
        placas_gtm.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "5. Generadora vacia"   

    if key ==6:  
        #6 PLACAS VS MAVVIAL    
        id_excp = list(placas_gtm.loc[placas_gtm['exclusion'].str.contains(r'\[6\]', na=False),'id']) 
                
        filtro = placas_gtm[(placas_gtm['cod_mun']==texto_filtro)]
        crs_proyectado = "EPSG:3116" 

        # 2. Crear copias temporales proyectadas
        placas_gtm_proj = filtro.to_crs(crs_proyectado)
        mv_gtm_proj = mv_gtm.to_crs(crs_proyectado)
        
        def buscar_2_mas_cercanos(punto_geom, lineas_gdf):
            # Buscamos líneas que intersecten un área de búsqueda (ej. 500 metros)
            buffer_busqueda = punto_geom.buffer(500).bounds 
            posibles_indices = list(lineas_gdf.sindex.intersection(buffer_busqueda))
            
            # Paso B: Si el buffer fue muy pequeño y no hay 2 líneas, comparamos con todas
            if len(posibles_indices) < 2:
                distancias = lineas_gdf.distance(punto_geom)
            else:
                # Solo calculamos la distancia real para los candidatos del índice
                candidatos = lineas_gdf.iloc[posibles_indices]
                distancias = candidatos.distance(punto_geom)
            
            # Paso C: Retornar los 2 menores
            top_2 = distancias.nsmallest(2)
            
            # Retornamos IDs de las líneas y sus distancias
            return pd.Series([top_2.index[0], top_2.iloc[0], top_2.index[1], top_2.iloc[1]])
        
        # 2. Aplicamos la función a cada punto
        resultados = placas_gtm_proj.geometry.apply(lambda x: buscar_2_mas_cercanos(x, mv_gtm_proj))

        # 3. Renombramos las columnas y unimos al original
        resultados.columns = ['mv_uno', 'dist_1_m', 'mv_dos', 'dist_2_m']
        filtro_final = pd.concat([filtro, resultados], axis=1)
        placas_gtm = pd.concat([placas_gtm, resultados[['mv_uno', 'mv_dos']]], axis=1)
        
        resultados_df = filtro_final.reset_index()[['index', 'mv_uno', 'mv_dos']]
        resultados_df.columns = ['placa', 'mv_uno', 'mv_dos']
        
        for row in resultados_df.itertuples(index=False):
            if placas_gtm.at[row[0],'id'] in id_excp:
                continue
            if not ((placas_gtm.at[row[0], 'tipovia']==mv_gtm.at[row[1], 'tipovia']) and (placas_gtm.at[row[0], 'nomvia']==mv_gtm.at[row[1], 'nomvia']) and (placas_gtm.at[row[0], 'generadora']==mv_gtm.at[row[1], 'generadora'])):
                if not ((placas_gtm.at[row[0], 'tipovia']==mv_gtm.at[row[2], 'tipovia']) and (placas_gtm.at[row[0], 'nomvia']==mv_gtm.at[row[2], 'nomvia']) and (placas_gtm.at[row[0], 'generadora']==mv_gtm.at[row[2], 'generadora'])):
                    #print(placas_gtm.at[row[0], 'id'])
                    if placas_gtm.at[row[0], 'incidencia'] is None:
                        placas_gtm.at[row[0], 'incidencia']='6. No corresponde la placa con el nombre de via'
                    else:
                        placas_gtm.at[row[0], 'incidencia']=placas_gtm.at[row[0], 'incidencia'] + ' - 6. No corresponde direccion con el de la via'
        
    if key ==7:   
        # 7 NUM PUERTA REPETIDO
        agrupados = placas_gtm[(placas_gtm['cod_mun']==texto_filtro)][['cod_zona','tipovia','nomvia','generadora']].dropna().drop_duplicates().reset_index(drop=True)
        copia_placas=placas_gtm[(placas_gtm['cod_mun']==texto_filtro)].dropna(subset=['cod_mun','cod_zona','tipovia','nomvia','generadora']).reset_index(drop=False).drop(['cod_mun'], axis=1).set_index(['cod_zona','tipovia','nomvia','generadora']).sort_index()
        repetidos_total=[]
        for row in agrupados.itertuples(index=False):
            filtro = copia_placas.loc[(row[0],row[1],row[2],row[3])].sort_values(by='placa').set_index('placa')
            indices = filtro.index.tolist()
            ind_repetidos = list(item for item in indices if indices.count(item) > 1)
            repetidos_total.extend(list(filtro.loc[ind_repetidos,'index']))
        #MARCAR ERRORES
        #MARCAR PUERTAS REPETIDAS
        repetidos_total=list(set(repetidos_total))
        cond1 = placas_gtm.index.isin(repetidos_total)
        cond2 = placas_gtm['incidencia'].isna()
        cond3 = placas_gtm['exclusion'].str.contains(r'\[7\]', na=False)
        placas_gtm.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_gtm['incidencia'] + " - 7. Numero de puerta repetido"
        placas_gtm.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "7. Numero de puerta repetido"

    if key ==8: 
        #8 COSTADO INCORRECTO Y 9 SALTO DE PLACAS >4    
        
        #AUX PARA CORRER PREDIOS
        idx_pr = indexx.Index()
        # Agregar poligonos al índice
        for i, geometry in enumerate(manzanas_gtm.geometry):
            if geometry is not None:
                idx_pr.insert(i, geometry.bounds)
                    
        agrupados = placas_gtm[(placas_gtm['cod_mun']==texto_filtro)][['cod_zona','tipovia','nomvia','generadora','placa']].dropna().drop('placa', axis=1).drop_duplicates().reset_index(drop=True)
        copia_placas=placas_gtm[(placas_gtm['cod_mun']==texto_filtro)][['cod_zona','tipovia','nomvia','generadora','placa','geom']].dropna().reset_index(drop=False).set_index(['cod_zona','tipovia','nomvia','generadora']).sort_index()
        copia_placas['placa']=copia_placas['placa'].apply(lambda x: int(re.sub(r'\D', '', x)))
        errores_total=[]
        saltos_total=[]
        for row in agrupados.itertuples(index=False):
            filtro = copia_placas.loc[(row[0],row[1],row[2],row[3])].sort_values(by='placa').set_index('placa')
            indices = filtro.index.tolist()
            pares = [num for num in indices if num % 2 == 0]
            impares = [num for num in indices if num % 2 != 0]
            if len(pares)>1:
                Error=False
            if len(pares)>1:
                rep=0
                ciclo = False
                for actual, siguiente in zip(pares, pares[1:]):
                    if actual == siguiente:
                        if rep==0:
                            conteo = (filtro.index == actual).sum()-1
                        linea = LineString([filtro.at[actual,'geom'].iloc[rep], filtro.at[siguiente,'geom'].iloc[rep+1]])
                        rep+=1
                        ciclo = True
                    else:
                        if ((filtro.index == siguiente).sum()-1)>0:
                            if (int(siguiente)-int(actual))>4:
                                saltos_total.extend(list(filtro.loc[siguiente,'index']))
                            pfinal=filtro.at[siguiente,'geom'].iloc[0]
                        else:
                            if (int(siguiente)-int(actual))>4:
                                saltos_total.append(filtro.at[siguiente,'index'])
                            pfinal=filtro.at[siguiente,'geom']
                        if ciclo == True:
                            linea = LineString([filtro.at[actual,'geom'].iloc[rep], pfinal])
                            ciclo = False
                            rep=0
                        else:
                            linea = LineString([filtro.at[actual,'geom'], pfinal])
                    candidates = list(idx.intersection(linea.bounds))
                    for i in candidates:
                        if linea.intersects(mv_gtm.geometry[i]):
                            errores_total.extend(list(filtro.loc[[actual,siguiente],'index']))
                            Error = True
                            break
                    if not Error:
                        candidates = list(idx_pr.intersection(linea.bounds))
                        cruce=0
                        for i in candidates:
                            if linea.intersects(manzanas_gtm.geometry[i]):
                                cruce += 1
                            if cruce == 3:
                                errores_total.extend(list(filtro.loc[[actual,siguiente],'index']))
                                break
            Error=False                
            if len(impares)>1:
                rep=0
                ciclo = False
                for actual, siguiente in zip(impares, impares[1:]):
                    if actual == siguiente:
                        if rep==0:
                            conteo = (filtro.index == actual).sum()-1
                        linea = LineString([filtro.at[actual,'geom'].iloc[rep], filtro.at[siguiente,'geom'].iloc[rep+1]])
                        rep+=1
                        ciclo = True
                    else:
                        if ((filtro.index == siguiente).sum()-1)>0:
                            if (int(siguiente)-int(actual))>4:
                                saltos_total.extend(list(filtro.loc[siguiente,'index']))
                            pfinal=filtro.at[siguiente,'geom'].iloc[0]
                        else:
                            if (int(siguiente)-int(actual))>4:
                                saltos_total.append(filtro.at[siguiente,'index'])
                            pfinal=filtro.at[siguiente,'geom']
                        if ciclo == True:
                            linea = LineString([filtro.at[actual,'geom'].iloc[rep], pfinal])
                            ciclo = False
                            rep=0
                        else:
                            linea = LineString([filtro.at[actual,'geom'], pfinal])
                    candidates = list(idx.intersection(linea.bounds))
                    for i in candidates:
                        if linea.intersects(mv_gtm.geometry[i]):
                            errores_total.extend(list(filtro.loc[[actual,siguiente],'index']))
                            Error = True
                            break
                    if not Error:
                        candidates = list(idx_pr.intersection(linea.bounds))
                        cruce=0
                        for i in candidates:
                            if linea.intersects(manzanas_gtm.geometry[i]):
                                cruce += 1
                            if cruce == 3:
                                errores_total.extend(list(filtro.loc[[actual,siguiente],'index']))
                                break

        #MARCAR ERRORES COSTADOS
        errores_total=list(set(errores_total))
        cond1 = placas_gtm.index.isin(errores_total)
        cond2 = placas_gtm['incidencia'].isna()
        cond3 = placas_gtm['incidencia'].str.contains(r'\[8\]', na=False)
        placas_gtm.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_gtm['incidencia'] + " - 8. Error costados"
        placas_gtm.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "8. Error costados"

        #MARCAR ERRORES SALTOS
        saltos_total=list(set(saltos_total))
        cond1 = placas_gtm.index.isin(saltos_total)
        cond2 = placas_gtm['incidencia'].isna()
        cond3 = placas_gtm['incidencia'].str.contains(r'\[9\]', na=False)
        placas_gtm.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_gtm['incidencia'] + " - 9. Salto de placa"
        placas_gtm.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "9. Salto de placa"
    
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
                            lista[i+1][2] = placas_gtm.loc[lista[i+1][0],'geom'] = Point(lista[i][2].x+emas,lista[i][2].y+nmas)
                            edicion.add(lista[i+1][0])
                        else:
                            if lista [i+1][3] is None:
                                lista [i+1][3]='Movido'
                                coordenadas.append([lista[i+1][0],str(geom_original.loc[lista[i+1][0],'geom'].wkt)])
                            if lista [i+2][3] is None:
                                lista [i+2][3]='Movido'
                                coordenadas.append([lista[i+2][0],str(geom_original.loc[lista[i+2][0],'geom'].wkt)])
                            placas_gtm.loc[lista[i+1][0],'geom'] = placas_gtm.loc[lista[i+2][0],'geom']
                            placas_gtm.loc[lista[i+2][0],'geom'] = lista[i+1][2]
                            lista[i+1][2] = placas_gtm.loc[lista[i+1][0],'geom']
                            lista[i+2][2] = placas_gtm.loc[lista[i+2][0],'geom']
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
                            lista[i+2][2] = placas_gtm.loc[lista[i+2][0],'geom'] = Point(lista[i+1][2].x+emas,lista[i+1][2].y+nmas)
                            edicion.add(lista[i+2][0])
                        else:
                            if lista [i+1][3] is None:
                                coordenadas.append([lista[i+1][0],str(geom_original.loc[lista[i+1][0],'geom'].wkt)])
                                lista [i+1][3]='Movido'
                            if lista [i+2][3] is None:
                                lista [i+2][3]='Movido'
                                coordenadas.append([lista[i+2][0],str(geom_original.loc[lista[i+2][0],'geom'].wkt)])
                            placas_gtm.loc[lista[i+1][0],'geom'] = placas_gtm.loc[lista[i+2][0],'geom']
                            placas_gtm.loc[lista[i+2][0],'geom'] = lista[i+1][2]
                            lista[i+1][2] = placas_gtm.loc[lista[i+1][0],'geom']
                            lista[i+2][2] = placas_gtm.loc[lista[i+2][0],'geom']
                            edicion.add(lista[i+1][0])
                            edicion.add(lista[i+2][0])
                    else:
                        if lista [i+1][3] is None:
                            coordenadas.append([lista[i+1][0],str(geom_original.loc[lista[i+1][0],'geom'].wkt)])
                            lista [i+1][3]='Movido'
                        if lista [i+2][3] is None:
                            lista [i+2][3]='Movido'
                            coordenadas.append([lista[i+2][0],str(geom_original.loc[lista[i+2][0],'geom'].wkt)])
                        placas_gtm.loc[lista[i+1][0],'geom'] = placas_gtm.loc[lista[i+2][0],'geom']
                        placas_gtm.loc[lista[i+2][0],'geom'] = lista[i+1][2]
                        lista[i+1][2] = placas_gtm.loc[lista[i+1][0],'geom']
                        lista[i+2][2] = placas_gtm.loc[lista[i+2][0],'geom']
                        edicion.add(lista[i+1][0])
                        edicion.add(lista[i+2][0])

        #Hallar agrupados
        geom_original=placas_gtm[['geom']].copy()
        placas_gtm=placas_gtm.to_crs(epsg=3857)
        copia_placas=placas_gtm[(placas_gtm['cod_mun']==texto_filtro) & (placas_gtm['exclusion'].isna())].dropna(subset=['cod_zona','nomvtotal','generadora','placa']).reset_index(drop=False).set_index(['cod_zona','nomvtotal','generadora']).sort_index()[['index','placa','geom','coord_ini']]#.to_crs(epsg=3857)
        copia_placas['placa'] = copia_placas['placa'].apply(lambda x: int(re.sub(r'\D', '', x)))
        edicion = set()
        coordenadas = []
        agrupados = placas_gtm[(placas_gtm['cod_mun']==texto_filtro) & (~placas_gtm['nomvtotal'].str.contains('S/N', na=False)) ][['cod_zona','nomvtotal','generadora','placa']].dropna().drop('placa', axis=1).drop_duplicates()
        for row in agrupados.itertuples(index=False):
            filtro = copia_placas.loc[(row[0],row[1],row[2])].sort_values(by='placa').set_index('placa')
            indices = filtro.index.tolist()
            pares = filtro[filtro.index % 2 == 0]
            impares = filtro[filtro.index % 2 != 0]
            if len(pares)>2:
                ordenar_placas(pares)
            if len(impares)>2:
                ordenar_placas(impares)
        placas_gtm=placas_gtm.to_crs(epsg=4326)

        #TRAER  COORDENADAS
        df = pd.DataFrame(coordenadas, columns=['idx', 'coorde'])
        merge = placas_gtm.join(df.set_index('idx'))
        merge['coord_ini'] = merge['coord_ini'].fillna(merge['coorde'])
        placas_gtm = merge.drop(columns=['coorde'])

        #MARCAR 
        cond1 = placas_gtm.index.isin(edicion)
        cond2 = placas_gtm['obs_qa'].isna()
        placas_gtm.loc[cond1 & ~cond2, 'obs_qa'] = placas_gtm['obs_qa'] + " - Posición modificada"
        placas_gtm.loc[cond1 & cond2, 'obs_qa'] = "Posición modificada"

        #Marca devolucion
        placas_gtm['edicion10']=None
        placas_gtm.loc[cond1,'edicion10'] = 'SI'
    return placas_gtm

def Gtm_validar_placas(engine, mavvial, placas, manzanas, texto_filtro, seleccionados):

    campos_1 = 'id,geom,nom_dep,nom_mun,nom_zona,nom_urb,tipovia,nomvia,direccion,atipico'
    campos_2 = 'id,geom,id_capa,atipico'
    campos_3 = 'id,geom,cod_dep,cod_mun,tipovia,atipico'
    campos_4 = 'id,geom,cod_dep,cod_mun,nomvia,atipico'
    campos_5 = 'id,geom,cod_dep,cod_mun,generadora,atipico'
    campos_6 = 'id,geom,cod_dep,cod_mun,tipovia,nomvia,generadora,atipico'
    campos_7 = 'id,geom,cod_dep,cod_mun,cod_zona,tipovia,nomvia,generadora,placa,atipico'
    campos_8 = 'id,geom,cod_dep,cod_mun,cod_zona,tipovia,nomvia,generadora,placa,atipico'
    campos_10 = 'id,geom,cod_dep,cod_mun,cod_zona,nomvtotal,generadora,placa,atipico,obs_qa,coord_ini'
    
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

    sql = f"SELECT {final_fields} FROM {placas} WHERE cod_mun = '{texto_filtro}';"
    placas_gtm = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
    placas_gtm['incidencia'] = None
    placas_gtm['exclusion'] = placas_gtm['atipico'].apply(
        lambda mi_string: ','.join([f"[{x}]" for x in mi_string.replace(" ", "").split(",")]) 
        if mi_string is not None else None
	)
    
    #Traer mv_gtm
    if (set(seleccionados) - {1,2,7,10}) != set():#Que no
        #TRAER MALLA
        sql=f"SELECT id, geom, tipovia, nomvia, generadora FROM {mavvial} WHERE cod_mun = '{texto_filtro}';"
        mv_gtm = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
        
        if ({3,4,5,6,8} & set(seleccionados)) != set():#Que si
            #AUX PARA CORRER MV
            idx = indexx.Index()
            # Agregar líneas al índice
            for i, geometry in enumerate(mv_gtm.geometry):
                if geometry is not None:
                    idx.insert(i, geometry.bounds)
        else:
            idx=''
                    
    else:
        mv_gtm=''
        idx=''
        
     
    #Si se necesita mas idx de predios mandar como parametro   
    ##AUX PARA CORRER PREDIOS
    #idx_pr = indexx.Index()
    ## Agregar poligonos al índice
    #for i, geometry in enumerate(manzanas_gtm.geometry):
    #    if geometry is not None:
    #        idx_pr.insert(i, geometry.bounds)   
        
        
    #Traer manzanas_gtm
    if ({8} & set(seleccionados)) != set():#Que si
        #TRAER PREDIOS
        sql=f"SELECT id, geom FROM {manzanas};"
        manzanas_gtm = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
        
    else:
        manzanas_gtm=''
    
    for key in seleccionados:
        placas_gtm = Gtm_pl_incidencia(mv_gtm, placas_gtm, manzanas_gtm, texto_filtro, key,idx)
        
    if 10 in seleccionados:
        if set(seleccionados) == {10}:
            df_temporal = placas_gtm[placas_gtm['edicion10'].notna()][['id','obs_qa','coord_ini','geom']]
        else:
            df_temporal = placas_gtm[placas_gtm['edicion10'].notna() | placas_gtm['incidencia'].notna()][['id','incidencia','obs_qa','coord_ini','geom']]
        df_temporal.to_postgis('tabla_temporal', con=engine, index=False, if_exists='replace')
    else:
        df_temporal = placas_gtm[placas_gtm['incidencia'].notna()][['id', 'incidencia']]
        df_temporal.to_sql('tabla_temporal', con=engine, index=False, if_exists='replace')