def Peru_QueryValplacas(placas):
    query = """
    REINDEX TABLE """ + placas + """;
    ANALYZE """ + placas + """;
    
    ALTER TABLE """ + placas + """ DROP COLUMN IF EXISTS incidencia;    
    ALTER TABLE """ + placas + """ ADD COLUMN IF NOT EXISTS incidencia varchar;
    ALTER TABLE """ + placas + """ ADD COLUMN IF NOT EXISTS coord_ini varchar;
    ALTER TABLE """ + placas + """ ADD COLUMN IF NOT EXISTS observ_pos varchar;
    
    ALTER TABLE """ + placas + """ ADD COLUMN IF NOT EXISTS atipico varchar;
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX REEMPLAZAR SIMBOLOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/  
    UPDATE """ + placas + """ SET nom_dep = regexp_replace(nom_dep, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_dep ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + placas + """ SET nom_prov = regexp_replace(nom_prov, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_prov ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + placas + """ SET nom_distri = regexp_replace(nom_distri, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_distri ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
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
    UPDATE """ + placas + """ SET nom_prov = TRIM(nom_prov) WHERE nom_prov <> TRIM(nom_prov);
    UPDATE """ + placas + """ SET nom_distri = TRIM(nom_distri) WHERE nom_distri <> TRIM(nom_distri);
    UPDATE """ + placas + """ SET nom_urb = TRIM(nom_urb) WHERE nom_urb <> TRIM(nom_urb);
    UPDATE """ + placas + """ SET tipovia = TRIM(tipovia) WHERE tipovia <> TRIM(tipovia);
    UPDATE """ + placas + """ SET nomvia = TRIM(nomvia) WHERE nomvia <> TRIM(nomvia);
    UPDATE """ + placas + """ SET direccion = TRIM(direccion) WHERE direccion <> TRIM(direccion);

    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR DOBLES ESPACIOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + placas + """ SET nom_dep = REPLACE(nom_dep,'  ',' ') WHERE nom_dep LIKE '%  %';
    UPDATE """ + placas + """ SET nom_prov = REPLACE(nom_prov,'  ',' ') WHERE nom_prov LIKE '%  %';
    UPDATE """ + placas + """ SET nom_distri = REPLACE(nom_distri,'  ',' ') WHERE nom_distri LIKE '%  %';
    UPDATE """ + placas + """ SET nom_urb = REPLACE(nom_urb,'  ',' ') WHERE nom_urb LIKE '%  %';
    UPDATE """ + placas + """ SET tipovia = REPLACE(tipovia,'  ',' ') WHERE tipovia LIKE '%  %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'  ',' ') WHERE nomvia LIKE '%  %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'  ',' ') WHERE direccion LIKE '%  %';
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX PASAR A MAYUSCULAS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + placas + """ SET nom_dep = UPPER(nom_dep) WHERE nom_dep <> UPPER(nom_dep);
    UPDATE """ + placas + """ SET nom_prov = UPPER(nom_prov) WHERE nom_prov <> UPPER(nom_prov);
    UPDATE """ + placas + """ SET nom_distri = UPPER(nom_distri) WHERE nom_distri <> UPPER(nom_distri);
    UPDATE """ + placas + """ SET nom_urb = UPPER(nom_urb) WHERE nom_urb <> UPPER(nom_urb);
    UPDATE """ + placas + """ SET tipovia = UPPER(tipovia) WHERE tipovia <> UPPER(tipovia);
    UPDATE """ + placas + """ SET nomvia = UPPER(nomvia) WHERE nomvia <> UPPER(nomvia);
    UPDATE """ + placas + """ SET direccion = UPPER(direccion) WHERE direccion <> UPPER(direccion);
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX REEMPLAZAR TILDES XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/ 

    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'Á','A') WHERE nomvia LIKE '%Á%';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'É','E') WHERE nomvia LIKE '%É%';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'Í','I') WHERE nomvia LIKE '%Í%';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'Ó','O') WHERE nomvia LIKE '%Ó%';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'Ú','U') WHERE nomvia LIKE '%Ú%';   
    
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
    
    /*TODO LO QUE SEA PRIMER,PRIMERA,1ER REEMPLAZAR POR NUMEROS*/
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'PRIMERA','1') WHERE nomvia LIKE '%PRIMERA %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'SEGUNDA','2') WHERE nomvia LIKE '%SEGUNDA %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'TERCERA','3') WHERE nomvia LIKE '%TERCERA %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'CUARTA','4') WHERE nomvia LIKE '%CUARTA %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'QUINTA','5') WHERE nomvia LIKE '%QUINTA %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'SEXTA','6') WHERE nomvia LIKE '%SEXTA %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'SEPTIMA','7') WHERE nomvia LIKE '%SEPTIMA %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'OCTAVA','8') WHERE nomvia LIKE '%OCTAVA %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'NOVENA','9') WHERE nomvia LIKE '%NOVENA %';
    
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'PRIMERA','1') WHERE direccion LIKE '%PRIMERA %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'SEGUNDA','2') WHERE direccion LIKE '%SEGUNDA %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'TERCERA','3') WHERE direccion LIKE '%TERCERA %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'CUARTA','4') WHERE direccion LIKE '%CUARTA %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'QUINTA','5') WHERE direccion LIKE '%QUINTA %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'SEXTA','6') WHERE direccion LIKE '%SEXTA %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'SEPTIMA','7') WHERE direccion LIKE '%SEPTIMA %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'OCTAVA','8') WHERE direccion LIKE '%OCTAVA %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'NOVENA','9') WHERE direccion LIKE '%NOVENA %';

    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'PRIMER','1') WHERE nomvia LIKE '%PRIMER %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'PRIMERO','1') WHERE nomvia LIKE '%PRIMERO %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'SEGUNDO','2') WHERE nomvia LIKE '%SEGUNDO %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'TERCERO','3') WHERE nomvia LIKE '%TERCERO %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'CUARTO','4') WHERE nomvia LIKE '%CUARTO %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'QUINTO','5') WHERE nomvia LIKE '%QUINTO %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'SEXTO','6') WHERE nomvia LIKE '%SEXTO %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'SEPTIMO','7') WHERE nomvia LIKE '%SEPTIMO %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'OCTAVO','8') WHERE nomvia LIKE '%OCTAVO %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'NOVENO','9') WHERE nomvia LIKE '%NOVENO %';
    
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'PRIMER','1') WHERE direccion LIKE '%PRIMER %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'PRIMERO','1') WHERE direccion LIKE '%PRIMERO %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'SEGUNDO','2') WHERE direccion LIKE '%SEGUNDO %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'TERCERO','3') WHERE direccion LIKE '%TERCERO %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'CUARTO','4') WHERE direccion LIKE '%CUARTO %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'QUINTO','5') WHERE direccion LIKE '%QUINTO %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'SEXTO','6') WHERE direccion LIKE '%SEXTO %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'SEPTIMO','7') WHERE direccion LIKE '%SEPTIMO %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'OCTAVO','8') WHERE direccion LIKE '%OCTAVO %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'NOVENO','9') WHERE direccion LIKE '%NOVENO %';

    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'UNO','1') WHERE nomvia LIKE '%UNO %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'DOS','2') WHERE nomvia LIKE '%DOS %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'TRES','3') WHERE nomvia LIKE '%TRES %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'CUATRO','4') WHERE nomvia LIKE '%CUATRO %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'CINCO','5') WHERE nomvia LIKE '%CINCO %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'SEIS','6') WHERE nomvia LIKE '%SEIS %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'SIETE','7') WHERE nomvia LIKE '%SIETE %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'OCHO','8') WHERE nomvia LIKE '%OCHO %';
    UPDATE """ + placas + """ SET nomvia = REPLACE(nomvia,'NUEVE','9') WHERE nomvia LIKE '%NUEVE %';
    
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'UNO','1') WHERE direccion LIKE '%UNO %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'DOS','2') WHERE direccion LIKE '%DOS %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'TRES','3') WHERE direccion LIKE '%TRES %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'CUATRO','4') WHERE direccion LIKE '%CUATRO %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'CINCO','5') WHERE direccion LIKE '%CINCO %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'SEIS','6') WHERE direccion LIKE '%SEIS %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'SIETE','7') WHERE direccion LIKE '%SIETE %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'OCHO','8') WHERE direccion LIKE '%OCHO %';
    UPDATE """ + placas + """ SET direccion = REPLACE(direccion,'NUEVE','9') WHERE direccion LIKE '%NUEVE %';   
    
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

def Peru_pl_incidencia(mv_peru, placas_peru, predios_peru, texto_filtro, key,idx):
    mifiltro=texto_filtro #####AQUI VA EL FILTRO#####
    partes = mifiltro.split(',')
    dep=partes[0]
    prov=partes[1]
    
    if key ==1:
        # 1. Validar registro con caracteres
        id_excp = list(placas_peru.loc[placas_peru['exclusion'].str.contains(r'\[1\]', na=False),'id'])
        # Expresión regular para caracteres especiales
        simbolos = r'[|!"#@$%&/()¿¡¨{}\[\]._:,;+\-*=/¬°]'

        # Función para marcar la inconsistencia si hay caracteres especiales en alguna columna específica
        def marcar_simbolos(row):
            if row['nomvia'] != 'S/N':
                columnas = ['nom_dep', 'nom_prov', 'nom_distri', 'nom_urb', 'tipovia', 'nomvia', 'direccion']
                for col in columnas:
                    if pd.notna(row[col]) and re.search(simbolos, row[col]) and (row['id'] not in id_excp):
                        return '1. Validar registro con caracteres - '
            return None

        # Aplicar la función para marcar incidencia
        placas_peru['incidencia'] = placas_peru.apply(marcar_simbolos, axis=1)   
        
    if key ==2:
        #2 PLACAS ID_CAPA REPETIDO
        frecuencias = placas_peru['id_capa'].value_counts().reset_index()
        valor_dict = frecuencias[frecuencias['count'] > 1].set_index('id_capa')['count'].to_dict()
        id_excp = list(placas_peru.loc[placas_peru['exclusion'].str.contains(r'\[2\]', na=False),'id'])
        placas_peru['incidencia'] = placas_peru.apply(
            lambda row: f"{row['incidencia']} - 2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['incidencia'] is not None and row['id_capa'] in valor_dict and row['id'] not in id_excp else 
            f"2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['incidencia'] is  None and row['id_capa'] in valor_dict and row['id'] not in id_excp  else
            row['incidencia'],
            axis=1
        )
        
    if key ==3:
        #3 PLACAS REFIJO
        id_excp = list(placas_peru.loc[placas_peru['exclusion'].str.contains(r'\[3\]', na=False),'id'])
        
        filtro = placas_peru[(placas_peru['cod_dep']==dep) & (placas_peru['cod_prov']==prov) & (placas_peru['tipovia'].isna())]
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=1))
            resultados.append([row.Index,candidates[0]])
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno'])
        tiponulo=[]
        #-------------------
        for row in resultados_df.itertuples(index=False):
            if placas_peru.at[row[0],'id'] in id_excp:
                continue
            if not (mv_peru.at[row[1], 'tipovia']==None):
                tiponulo.append(row[0])
                
        cond1 = placas_peru.index.isin(tiponulo)
        cond2 = placas_peru['incidencia'].isna()
        cond3 = placas_peru['exclusion'].str.contains(r'\[3\]', na=False)
        placas_peru.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_peru['incidencia'] + " - 3. Tipovia vacio"
        placas_peru.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "3. Tipovia vacio"   
    
    if key ==4:
        #4 VIA VACIA
        id_excp = list(placas_peru.loc[placas_peru['exclusion'].str.contains(r'\[4\]', na=False),'id'])
                
        filtro = placas_peru[(placas_peru['cod_dep']==dep) & (placas_peru['cod_prov']==prov) & ((placas_peru['nomvia'].isna()) | (placas_peru['nomvia'] == 'S/N'))]
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=1))
            resultados.append([row.Index,candidates[0]])
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno'])
        nomnulo=[]
        #-------------------
        for row in resultados_df.itertuples(index=False):
            if placas_peru.at[row[0],'id'] in id_excp:
                continue
            if mv_peru.at[row[1], 'nomvia'] is not None and mv_peru.at[row[1], 'nomvia'] != 'S/N':
                nomnulo.append(row[0])
                
        cond1 = placas_peru.index.isin(nomnulo)
        cond2 = placas_peru['incidencia'].isna()
        cond3 = placas_peru['exclusion'].str.contains(r'\[4\]', na=False)
        placas_peru.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_peru['incidencia'] + " - 4. nombre via vacio"
        placas_peru.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "4. Nombre via vacio"   
        
        
    if key ==5:
        #5 generadora VACIA
        id_excp = list(placas_peru.loc[placas_peru['exclusion'].str.contains(r'\[5\]', na=False),'id'])
                
        filtro = placas_peru[(placas_peru['cod_dep']==dep) & (placas_peru['cod_prov']==prov) & (placas_peru['generadora'].isna())]
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=1))
            resultados.append([row.Index,candidates[0]])
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno'])
        gennula=[]
        #-------------------
        for row in resultados_df.itertuples(index=False):
            if placas_peru.at[row[0],'id'] in id_excp:
                continue
            if not (mv_peru.at[row[1], 'generadora']==None):
                gennula.append(row[0])
                
        cond1 = placas_peru.index.isin(gennula)
        cond2 = placas_peru['incidencia'].isna()
        cond3 = placas_peru['exclusion'].str.contains(r'\[5\]', na=False)
        placas_peru.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_peru['incidencia'] + " - 5. Generadora vacia"
        placas_peru.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "5. Generadora vacia"   

    if key ==6:  
        #6 PLACAS VS MAVVIAL    
        id_excp = list(placas_peru.loc[placas_peru['exclusion'].str.contains(r'\[6\]', na=False),'id']) 
                
        filtro = placas_peru[(placas_peru['cod_dep']==dep) & (placas_peru['cod_prov']==prov)]
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=2))
            resultados.append([row.Index,candidates[0],candidates[1]])
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno','mv_dos'])
        #-------------------
        for row in resultados_df.itertuples(index=False):
            if placas_peru.at[row[0],'id'] in id_excp:
                continue
            if not ((placas_peru.at[row[0], 'tipovia']==mv_peru.at[row[1], 'tipovia']) and (placas_peru.at[row[0], 'nomvia']==mv_peru.at[row[1], 'nomvia']) and (placas_peru.at[row[0], 'generadora']==mv_peru.at[row[1], 'generadora'])):
                if not ((placas_peru.at[row[0], 'tipovia']==mv_peru.at[row[2], 'tipovia']) and (placas_peru.at[row[0], 'nomvia']==mv_peru.at[row[2], 'nomvia']) and (placas_peru.at[row[0], 'generadora']==mv_peru.at[row[2], 'generadora'])):
                    if placas_peru.at[row[0], 'incidencia'] is None:
                        placas_peru.at[row[0], 'incidencia']='6. No corresponde la placa con el nombre de via'
                    else:
                        placas_peru.at[row[0], 'incidencia']=placas_peru.at[row[0], 'incidencia'] + ' - 6. No corresponde direccion con el de la via'

    if key ==7:   
        # 7 NUM PUERTA REPETIDO
        agrupados = placas_peru[(placas_peru['cod_dep']==dep) & (placas_peru['cod_prov']==prov)][['cod_distri','tipovia','nomvia','generadora']].dropna().drop_duplicates().reset_index(drop=True)
        copia_placas=placas_peru[(placas_peru['cod_dep']==dep) & (placas_peru['cod_prov']==prov)].dropna(subset=['cod_dep', 'cod_prov','cod_distri','tipovia','nomvia','generadora']).reset_index(drop=False).drop(['cod_dep', 'cod_prov'], axis=1).set_index(['cod_distri','tipovia','nomvia','generadora']).sort_index()
        repetidos_total=[]
        for row in agrupados.itertuples(index=False):
            filtro = copia_placas.loc[(row[0],row[1],row[2],row[3])].sort_values(by='placa').set_index('placa')
            indices = filtro.index.tolist()
            ind_repetidos = list(item for item in indices if indices.count(item) > 1)
            repetidos_total.extend(list(filtro.loc[ind_repetidos,'index']))
        #MARCAR ERRORES
        #MARCAR PUERTAS REPETIDAS
        repetidos_total=list(set(repetidos_total))
        cond1 = placas_peru.index.isin(repetidos_total)
        cond2 = placas_peru['incidencia'].isna()
        cond3 = placas_peru['exclusion'].str.contains(r'\[7\]', na=False)
        placas_peru.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_peru['incidencia'] + " - 7. Numero de puerta repetido"
        placas_peru.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "7. Numero de puerta repetido"   

    if key ==8: 
        #8 COSTADO INCORRECTO Y 9 SALTO DE PLACAS >4    
        
        #AUX PARA CORRER PREDIOS
        idx_pr = indexx.Index()
        # Agregar poligonos al índice
        for i, geometry in enumerate(predios_peru.geometry):
            if geometry is not None:
                idx_pr.insert(i, geometry.bounds)
                    
        agrupados = placas_peru[(placas_peru['cod_dep']==dep) & (placas_peru['cod_prov']==prov)][['cod_distri','tipovia','nomvia','generadora','placa']].dropna().drop('placa', axis=1).drop_duplicates().reset_index(drop=True)
        copia_placas=placas_peru[(placas_peru['cod_dep']==dep) & (placas_peru['cod_prov']==prov)][['cod_distri','tipovia','nomvia','generadora','placa','geom']].dropna().reset_index(drop=False).set_index(['cod_distri','tipovia','nomvia','generadora']).sort_index()
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
                        if linea.intersects(mv_peru.geometry[i]):
                            errores_total.extend(list(filtro.loc[[actual,siguiente],'index']))
                            Error = True
                            break
                    if not Error:
                        candidates = list(idx_pr.intersection(linea.bounds))
                        cruce=0
                        for i in candidates:
                            if linea.intersects(predios_peru.geometry[i]):
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
                        if linea.intersects(mv_peru.geometry[i]):
                            errores_total.extend(list(filtro.loc[[actual,siguiente],'index']))
                            Error = True
                            break
                    if not Error:
                        candidates = list(idx_pr.intersection(linea.bounds))
                        cruce=0
                        for i in candidates:
                            if linea.intersects(predios_peru.geometry[i]):
                                cruce += 1
                            if cruce == 3:
                                errores_total.extend(list(filtro.loc[[actual,siguiente],'index']))
                                break

        #MARCAR ERRORES COSTADOS
        errores_total=list(set(errores_total))
        cond1 = placas_peru.index.isin(errores_total)
        cond2 = placas_peru['incidencia'].isna()
        cond3 = placas_peru['incidencia'].str.contains(r'\[8\]', na=False)
        placas_peru.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_peru['incidencia'] + " - 8. Error costados"
        placas_peru.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "8. Error costados"

        #MARCAR ERRORES SALTOS
        saltos_total=list(set(saltos_total))
        cond1 = placas_peru.index.isin(saltos_total)
        cond2 = placas_peru['incidencia'].isna()
        cond3 = placas_peru['incidencia'].str.contains(r'\[9\]', na=False)
        placas_peru.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = placas_peru['incidencia'] + " - 9. Salto de placa"
        placas_peru.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "9. Salto de placa"
    
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
                            lista[i+1][2] = placas_peru.loc[lista[i+1][0],'geom'] = Point(lista[i][2].x+emas,lista[i][2].y+nmas)
                            edicion.add(lista[i+1][0])
                        else:
                            if lista [i+1][3] is None:
                                lista [i+1][3]='Movido'
                                coordenadas.append([lista[i+1][0],str(geom_original.loc[lista[i+1][0],'geom'].wkt)])
                            if lista [i+2][3] is None:
                                lista [i+2][3]='Movido'
                                coordenadas.append([lista[i+2][0],str(geom_original.loc[lista[i+2][0],'geom'].wkt)])
                            placas_peru.loc[lista[i+1][0],'geom'] = placas_peru.loc[lista[i+2][0],'geom']
                            placas_peru.loc[lista[i+2][0],'geom'] = lista[i+1][2]
                            lista[i+1][2] = placas_peru.loc[lista[i+1][0],'geom']
                            lista[i+2][2] = placas_peru.loc[lista[i+2][0],'geom']
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
                            lista[i+2][2] = placas_peru.loc[lista[i+2][0],'geom'] = Point(lista[i+1][2].x+emas,lista[i+1][2].y+nmas)
                            edicion.add(lista[i+2][0])
                        else:
                            if lista [i+1][3] is None:
                                coordenadas.append([lista[i+1][0],str(geom_original.loc[lista[i+1][0],'geom'].wkt)])
                                lista [i+1][3]='Movido'
                            if lista [i+2][3] is None:
                                lista [i+2][3]='Movido'
                                coordenadas.append([lista[i+2][0],str(geom_original.loc[lista[i+2][0],'geom'].wkt)])
                            placas_peru.loc[lista[i+1][0],'geom'] = placas_peru.loc[lista[i+2][0],'geom']
                            placas_peru.loc[lista[i+2][0],'geom'] = lista[i+1][2]
                            lista[i+1][2] = placas_peru.loc[lista[i+1][0],'geom']
                            lista[i+2][2] = placas_peru.loc[lista[i+2][0],'geom']
                            edicion.add(lista[i+1][0])
                            edicion.add(lista[i+2][0])
                    else:
                        if lista [i+1][3] is None:
                            coordenadas.append([lista[i+1][0],str(geom_original.loc[lista[i+1][0],'geom'].wkt)])
                            lista [i+1][3]='Movido'
                        if lista [i+2][3] is None:
                            lista [i+2][3]='Movido'
                            coordenadas.append([lista[i+2][0],str(geom_original.loc[lista[i+2][0],'geom'].wkt)])
                        placas_peru.loc[lista[i+1][0],'geom'] = placas_peru.loc[lista[i+2][0],'geom']
                        placas_peru.loc[lista[i+2][0],'geom'] = lista[i+1][2]
                        lista[i+1][2] = placas_peru.loc[lista[i+1][0],'geom']
                        lista[i+2][2] = placas_peru.loc[lista[i+2][0],'geom']
                        edicion.add(lista[i+1][0])
                        edicion.add(lista[i+2][0])

        #Hallar agrupados
        geom_original=placas_peru[['geom']].copy()
        placas_peru=placas_peru.to_crs(epsg=3857)
        copia_placas=placas_peru[(placas_peru['cod_dep']==dep) & (placas_peru['cod_prov']==prov) & (placas_peru['exclusion'].isna())].dropna(subset=['cod_distri','nomvtotal','generadora','placa']).reset_index(drop=False).set_index(['cod_distri','nomvtotal','generadora']).sort_index()[['index','placa','geom','coord_ini']]#.to_crs(epsg=3857)
        copia_placas['placa'] = copia_placas['placa'].apply(lambda x: int(re.sub(r'\D', '', x)))
        edicion = set()
        coordenadas = []
        agrupados = placas_peru[(placas_peru['cod_dep']==dep) & (placas_peru['cod_prov']==prov) & (~placas_peru['nomvtotal'].str.contains('S/N', na=False)) ][['cod_distri','nomvtotal','generadora','placa']].dropna().drop('placa', axis=1).drop_duplicates()
        for row in agrupados.itertuples(index=False):
            filtro = copia_placas.loc[(row[0],row[1],row[2])].sort_values(by='placa').set_index('placa')
            indices = filtro.index.tolist()
            pares = filtro[filtro.index % 2 == 0]
            impares = filtro[filtro.index % 2 != 0]
            if len(pares)>2:
                ordenar_placas(pares)
            if len(impares)>2:
                ordenar_placas(impares)
        placas_peru=placas_peru.to_crs(epsg=4326)

        #TRAER  COORDENADAS
        df = pd.DataFrame(coordenadas, columns=['idx', 'coorde'])
        merge = placas_peru.join(df.set_index('idx'))
        merge['coord_ini'] = merge['coord_ini'].fillna(merge['coorde'])
        placas_peru = merge.drop(columns=['coorde'])

        #MARCAR 
        cond1 = placas_peru.index.isin(edicion)
        cond2 = placas_peru['observ_pos'].isna()
        placas_peru.loc[cond1 & ~cond2, 'observ_pos'] = placas_peru['observ_pos'] + " - Posición modificada"
        placas_peru.loc[cond1 & cond2, 'observ_pos'] = "Posición modificada"

        #Marca devolucion
        placas_peru['edicion10']=None
        placas_peru.loc[cond1,'edicion10'] = 'SI'
    return placas_peru

def Peru_validar_placas(engine, mavvial, placas, predios, texto_filtro, seleccionados):

    mifiltro=texto_filtro #####AQUI VA EL FILTRO#####
    partes = mifiltro.split(',')
    dep=partes[0]
    prov=partes[1]

    campos_1 = 'id,geom,nom_dep,nom_prov,nom_distri,nom_urb,tipovia,nomvia,direccion,atipico'
    campos_2 = 'id,geom,id_capa,atipico'
    campos_3 = 'id,geom,cod_dep,cod_prov,tipovia,atipico'
    campos_4 = 'id,geom,cod_dep,cod_prov,nomvia,atipico'
    campos_5 = 'id,geom,cod_dep,cod_prov,generadora,atipico'
    campos_6 = 'id,geom,cod_dep,cod_prov,tipovia,nomvia,generadora,placa,atipico'
    campos_7 = 'id,geom,cod_dep,cod_prov,cod_distri,tipovia,nomvia,generadora,placa,atipico'
    campos_8 = 'id,geom,cod_dep,cod_prov,cod_distri,tipovia,nomvia,generadora,placa,atipico'
    campos_10 = 'id,geom,cod_dep,cod_prov,cod_distri,nomvtotal,generadora,placa,atipico,observ_pos,coord_ini'
    
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

    sql = f"SELECT {final_fields} FROM {placas} WHERE cod_dep = '{dep}' AND cod_prov = '{prov}';"
    placas_peru = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
    placas_peru['incidencia'] = None
    placas_peru['exclusion'] = placas_peru['atipico'].apply(
        lambda mi_string: ','.join([f"[{x}]" for x in mi_string.replace(" ", "").split(",")]) 
        if mi_string is not None else None
	)
    
    #Traer mv_peru
    if (set(seleccionados) - {1,2,7,10}) != set():#Que no
        #TRAER MALLA
        sql=f"SELECT id, geom, tipovia, nomvia, generadora FROM {mavvial} WHERE cod_dep = '{dep}' AND cod_prov = '{prov}';"
        mv_peru = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
        
        if ({3,4,5,6,8} & set(seleccionados)) != set():#Que si
            #AUX PARA CORRER MV
            idx = indexx.Index()
            # Agregar líneas al índice
            for i, geometry in enumerate(mv_peru.geometry):
                if geometry is not None:
                    idx.insert(i, geometry.bounds)
        else:
            idx=''
                    
    else:
        mv_peru=''
        idx=''
        
     
    #Si se necesita mas idx de predios mandar como parametro   
    ##AUX PARA CORRER PREDIOS
    #idx_pr = indexx.Index()
    ## Agregar poligonos al índice
    #for i, geometry in enumerate(predios_peru.geometry):
    #    if geometry is not None:
    #        idx_pr.insert(i, geometry.bounds)   
        
        
    #Traer predios_peru
    if ({8} & set(seleccionados)) != set():#Que si
        #TRAER PREDIOS
        sql=f"SELECT id, geom FROM {predios};"
        predios_peru = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
        
    else:
        predios_peru=''
    
    for key in seleccionados:
        placas_peru = Peru_pl_incidencia(mv_peru, placas_peru, predios_peru, texto_filtro, key,idx)
        
    if 10 in seleccionados:
        if set(seleccionados) == {10}:
            df_temporal = placas_peru[placas_peru['edicion10'].notna()][['id','observ_pos','coord_ini','geom']]
        else:
            df_temporal = placas_peru[placas_peru['edicion10'].notna() | placas_peru['incidencia'].notna()][['id','incidencia','observ_pos','coord_ini','geom']]
        df_temporal.to_postgis('tabla_temporal', con=engine, index=False, if_exists='replace')
    else:
        df_temporal = placas_peru[placas_peru['incidencia'].notna()][['id', 'incidencia']]
        df_temporal.to_sql('tabla_temporal', con=engine, index=False, if_exists='replace')