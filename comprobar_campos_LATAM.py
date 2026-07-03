import pandas as pd
import numpy as np


def validar_campos(engine,bd,tablas):

    capas = []
    NOMVTOTAL_sobran = []
    NOMVTOTAL_faltan = []
    NOMVTOTAL_tipo = []
    NOMVTOTAL_lon = []
    
    if 'peru' in bd.lower():
        for tabla in tablas:
            if tabla[0:8] == 'distrito':
                capa = tabla
                
                #1 ESTRUCTURAS DISTRITOS
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'Integer', 9],
                    ['UBIGEO', 'character varying', 80],
                    ['COD_DEP', 'character varying', 80],
                    ['NOM_DEP', 'character varying', 80],
                    ['COD_PROV', 'character varying', 80],
                    ['NOM_PROV', 'character varying', 80],
                    ['COD_DRISTRI', 'character varying', 80],
                    ['NOM_DRISTRI', 'character varying', 80],
                    ['MARCA', 'character varying', 5],
                    ['FECHA', 'character varying', 10],
                    ['VERSION', 'character varying', 5],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql

                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()
                
                capas.append(capa)         
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)

            elif tabla[0:11] == 'hidrografia':
                capa = tabla
                
                #1 ESTRUCTURA ESTRUCTURA HIDROGRAFIA
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'Integer', 9],
                    ['UBIGEO', 'character varying', 80],
                    ['NOM_HIDRO', 'character varying', 80],
                    ['NOM_DEP', 'character varying', 80],
                    ['NOM_PROV', 'character varying', 80],
                    ['NOM_DRISTRI', 'character varying', 80],
                    ['CLASIFICAC', 'character varying', 80],
                    ['MARCA', 'character varying', 5],
                    ['FECHA', 'character varying', 10],
                    ['VERSION', 'character varying', 5],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql

                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()

                capas.append(capa)       
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)
                
            elif tabla[0:8] == 'manzanas':
                capa = tabla
            
                #1 ESTRUCTURA MANZANAS
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'Integer', 9],
                    ['UBIGEO', 'character varying', 80],
                    ['COD_DEP', 'character varying', 80],
                    ['NOM_DEP', 'character varying', 80],
                    ['COD_PROV', 'character varying', 80],
                    ['NOM_PROV', 'character varying', 80],
                    ['COD_DRISTRI', 'character varying', 80],
                    ['NOM_DRISTRI', 'character varying', 80],
                    ['COD_URB', 'character varying', 80],
                    ['NOM_URB', 'character varying', 80],
                    ['ZONA', 'character varying', 5],
                    ['MANZANA', 'character varying', 4],
                    ['ID_MANZANA', 'character varying', 20],
                    ['ESTRATO', 'character varying', 5],
                    ['CODMZINEI', 'character varying', 80],
                    ['MARCA', 'character varying', 5],
                    ['FECHA', 'character varying', 10],
                    ['VERSION', 'character varying', 5],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql
                
                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()
                
                capas.append(capa)       
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)
                
            elif tabla[0:7] == 'mavvial':           
              
                capa = tabla
                
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                ORDER BY 
                    ordinal_position;"""
                    
                columnas_psql = pd.read_sql(sql, engine)
                
                data = [
                    ['ID_CAPA', 'Integer', 9],
                    ['UBIGEO', 'character varying', 80],
                    ['COD_DEP', 'character varying', 80],
                    ['NOM_DEP', 'character varying', 80],
                    ['COD_PROV', 'character varying', 80],
                    ['NOM_PROV', 'character varying', 80],
                    ['COD_DRISTRI', 'character varying', 80],
                    ['NOM_DRISTRI', 'character varying', 80],
                    ['COD_URB', 'character varying', 80],
                    ['NOM_URB', 'character varying', 80],
                    ['COSTADO', 'character varying', 2],
                    ['TIPOVIA', 'character varying', 2],
                    ['NOMVIA', 'character varying', 60],
                    ['NOMVTOTAL', 'character varying', 70],
                    ['GENERADORA', 'character varying', 10],
                    ['ONEWAY', 'character varying', 5],
                    ['VELOCIDAD', 'character varying', 5],
                    ['CONTROL', 'character varying', 20],
                    ['INICIOIZQ', 'numeric', 20],
                    ['FINIZQ', 'numeric', 20],
                    ['INICIODER', 'numeric', 20],
                    ['FINDER', 'numeric', 20],
                    ['COD_POST', 'character varying', 80],
                    ['MARCA', 'character varying', 5],
                    ['FECHA', 'character varying', 10],
                    ['VERSION', 'character varying', 5],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql
                """if len(col_sobran)>0:
                    print('Estas columnas sobran',list(col_sobran))
                if len(col_faltan)>0:
                    print('Estas columnas faltan',list(col_faltan))"""
                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                #print('Los campos que tiene diferente tipo a la estructura son:',dif_tipo)
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()
                #print('Los campos que tiene diferente longitud a la estructura son:',dif_lon)

                capas.append(capa)            
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)
                
            elif tabla[0:6] == 'mzacas':
                capa = tabla
            
                #1 ESTRUCTURA MZACASA
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'numeric', 19],
                    ['UBIGEO', 'character varying', 80],
                    ['COD_DEP', 'character varying', 80],
                    ['NOM_DEP', 'character varying', 254],
                    ['COD_PROV', 'character varying', 80],
                    ['NOM_PROV', 'character varying', 254],
                    ['COD_DRISTRI', 'character varying', 80],
                    ['NOM_DRISTRI', 'character varying', 254],
                    ['COD_URB', 'character varying', 80],
                    ['NOM_URB', 'character varying', 80],
                    ['NOMVIA', 'character varying', 120],
                    ['NUMPUERTA', 'character varying', 50],
                    ['NOMVIA_2', 'character varying', 120],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql

                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()
                
                capas.append(capa)  
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)

            elif tabla[0:11] == 'nmzcs':
                capa = tabla
            
                #1 ESTRUCTURA PTOS_NMZCASA
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'numeric', 19],
                    ['UBIGEO', 'character varying', 80],
                    ['COD_DEP', 'character varying', 80],
                    ['NOM_DEP', 'character varying', 254],
                    ['COD_PROV', 'character varying', 80],
                    ['NOM_PROV', 'character varying', 254],
                    ['COD_DRISTRI', 'character varying', 80],
                    ['NOM_DRISTRI', 'character varying', 254],
                    ['COD_URB', 'character varying', 80],
                    ['NOM_URB', 'character varying', 80],
                    ['TIPOVIA', 'character varying', 3],
                    ['NOMVIA', 'character varying', 50],
                    ['NOMVTOTAL', 'character varying', 60],
                    ['NUMPUERTA', 'character varying', 50],
                    ['MANZANA', 'character varying', 10],                
                    ['LOTE', 'character varying', 10],                
                    ['URBANIZACI', 'character varying', 100],                
                    ['CATEGORIA', 'character varying', 10],               
                    ['NOMVTOTALIZA', 'character varying', 100],                
                    ['PRIORIDAD', 'character varying', 2],                
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql

                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()
                
                capas.append(capa)            
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)   
                
            elif tabla[0:7] == 'parques':
                capa = tabla
            
                #1 ESTRUCTURA PARQUES_Y_ZONAS_VERDES
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'numeric', 19],
                    ['UBIGEO', 'character varying', 80],
                    ['COD_DEP', 'character varying', 80],
                    ['NOM_DEP', 'character varying', 254],
                    ['COD_PROV', 'character varying', 80],
                    ['NOM_PROV', 'character varying', 254],
                    ['COD_DRISTRI', 'character varying', 80],
                    ['NOM_DRISTRI', 'character varying', 254],
                    ['COD_URB', 'character varying', 80],
                    ['NOM_URB', 'character varying', 80],
                    ['NOMVIA', 'character varying', 80],
                    ['MARCA', 'character varying', 5],
                    ['FECHA', 'character varying', 10],
                    ['VERSION', 'character varying', 5],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql

                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()

                
                capas.append(capa)       
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)
                
            elif tabla[0:2] == 'ph':
                capa = tabla
                
                #1 ESTRUCTURA ESTRUCTURA PH_TELEFONICA
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'Integer', 16],
                    ['DIRECCION', 'character varying', 254],
                    ['TIPO_DIREC', 'character varying', 80],
                    ['DIRECCIO_2', 'character varying', 254],
                    ['LAYER', 'character varying', 80],
                    ['X', 'Double', 11],
                    ['Y', 'Double', 11],
                    ['FID', 'Integer', 11],
                    ['NEWFIELD1', 'character varying', 100],
                    ['COUNT', 'Integer', 11],
                    ['FIRST_IDCA', 'Integer', 11],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql

                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()
                    
                capas.append(capa)         
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)
                
            elif tabla[0:6] == 'placas':
                capa = tabla
            
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'Integer', 20],
                    ['UBIGEO', 'character varying', 6],
                    ['COD_DEP', 'character varying', 80],
                    ['NOM_DEP', 'character varying', 254],
                    ['COD_PROV', 'character varying', 80],
                    ['NOM_PROV', 'character varying', 254],
                    ['COD_DRISTRI', 'character varying', 80],
                    ['NOM_DRISTRI', 'character varying', 254],
                    ['COD_URB', 'character varying', 80],
                    ['NOM_URB', 'character varying', 80],
                    ['TIPOVIA', 'character varying', 5],
                    ['NOMVIA', 'character varying', 50],
                    ['MANZANA', 'character varying', 10],
                    ['LOTE', 'character varying', 80],
                    ['GENERADORA', 'character varying', 254],
                    ['TIPO_DIR', 'character varying', 80],
                    ['DIRECCION', 'character varying', 80],
                    ['ID_MAVVIAL', 'numeric', 20],
                    ['COD_POSTAL', 'character varying', 80],
                    ['MARCA', 'character varying', 5],
                    ['FECHA', 'character varying', 10],
                    ['VERSION', 'character varying', 5],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql
                """if len(col_sobran)>0:
                    print('Estas columnas sobran',list(col_sobran))#####IMPRIMIR#####
                if len(col_faltan)>0:
                    print('Estas columnas faltan',list(col_faltan))#####IMPRIMIR#####"""
                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                """if len(dif_tipo)>0:
                    print('Los campos que tiene diferente tipo a la estructura son:',dif_tipo)#####IMPRIMIR#####"""
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()
                """if len(dif_lon)>0:
                    print('Los campos que tiene diferente longitud a la estructura son:',dif_lon)#####IMPRIMIR#####"""  
                
                capas.append(capa)
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)
                
            elif tabla[0:7] == 'predios':
                capa = tabla
                #1 ESTRUCTURA PREDIOS
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'numeric', 20],
                    ['UBIGEO', 'character varying', 6],
                    ['COD_DEP', 'character varying', 80],
                    ['NOM_DEP', 'character varying', 80],
                    ['COD_PROV', 'character varying', 80],
                    ['NOM_PROV', 'character varying', 60],
                    ['COD_DRISTRI', 'character varying', 80],
                    ['NOM_DRISTRI', 'character varying', 80],
                    ['COD_URB', 'character varying', 80],
                    ['NOM_URB', 'character varying', 80],
                    ['NOM_CAT', 'character varying', 50],
                    ['NOM_NNUU', 'character varying', 100],
                    ['ESTRATF', 'character varying', 1],
                    ['NOMVIAEDIF', 'character varying', 150],
                    ['CODPREDIOP', 'character varying', 50],
                    ['NOMVIAMANZ', 'character varying', 30],
                    ['NOMVIAVIVI', 'character varying', 150],
                    ['MARCA', 'character varying', 5],
                    ['FECHA', 'character varying', 10],
                    ['VERSION', 'character varying', 5],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql

                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()
                
                capas.append(capa)
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)
                         
                
            elif tabla[0:9] == 'provincia':
                capa = tabla
            
                #1 ESTRUCTURA PROVINCIAS
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'Integer', 9],
                    ['NOM_DEP', 'character varying', 80],
                    ['COD_DEP', 'character varying', 80],
                    ['NOM_PROV', 'character varying', 80],
                    ['COD_PROV', 'character varying', 80],
                    ['MARCA', 'character varying', 5],
                    ['FECHA', 'character varying', 10],
                    ['VERSION', 'character varying', 5],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql

                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()
                
                capas.append(capa)          
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)
                
            elif tabla[0:12] == 'urbanizacion':
                capa = tabla
            
                #1 ESTRUCTURA URBANIZACIONES
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'Integer', 9],
                    ['UBIGEO', 'character varying', 80],
                    ['NOM_DRISTRI', 'character varying', 80],
                    ['COD_URB', 'character varying', 80],
                    ['CATE_URB', 'character varying', 50],
                    ['NOM_URB', 'character varying', 80],
                    ['MARCA', 'character varying', 5],
                    ['FECHA', 'character varying', 10],
                    ['VERSION', 'character varying', 5],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql

                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()
                
                capas.append(capa)         
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)

            elif tabla[0:8] == 'viasprin':
                capa = tabla
            
                #1 ESTRUCTURA VIASPRIN
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'Integer', 9],
                    ['UBIGEO', 'character varying', 80],
                    ['COD_DEP', 'character varying', 80],
                    ['NOM_DEP', 'character varying', 80],
                    ['COD_PROV', 'character varying', 80],
                    ['NOM_PROV', 'character varying', 80],
                    ['COD_DRISTRI', 'character varying', 80],
                    ['NOM_DRISTRI', 'character varying', 80],
                    ['COD_URB', 'character varying', 80],
                    ['NOM_URB', 'character varying', 80],
                    ['CLASIFICAC', 'character varying', 80],
                    ['NOMVIA', 'character varying', 80],
                    ['NOMVIA_2', 'character varying', 80],
                    ['MARCA', 'character varying', 5],
                    ['FECHA', 'character varying', 10],
                    ['VERSION', 'character varying', 5],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql

                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()
                
                capas.append(capa)          
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)
                
            elif tabla[0:14] == 'zonas_censales':
                capa = tabla

                #1 ESTRUCTURA ZONAS CENSALES
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'Integer', 9],
                    ['UBIGEO', 'character varying', 80],
                    ['ZONA_CENSA', 'character varying', 80],
                    ['MARCA', 'character varying', 5],
                    ['FECHA', 'character varying', 10],
                    ['VERSION', 'character varying', 5],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql

                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()
                
                capas.append(capa)         
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)
                
            elif tabla[0:14] == 'zonas_postales':
                capa = tabla

                #1 ESTRUCTURA ZONAS POSTALES
                sql=f"""SELECT 
                    column_name,
                    data_type as dt_psql,
                    character_maximum_length AS lon_psql
                FROM 
                    information_schema.columns
                WHERE 
                    table_name = '"""+tabla+"""'
                AND 
                    column_name!='inconsistencias'
                ORDER BY 
                    ordinal_position;"""
                columnas_psql = pd.read_sql(sql, engine)
                data = [
                    ['ID_CAPA', 'Integer', 9],
                    ['UBIGEO', 'character varying', 80],
                    ['COD_DEP', 'character varying', 80],
                    ['NOM_DEP', 'character varying', 80],
                    ['COD_PROV', 'character varying', 80],
                    ['NOM_PROV', 'character varying', 80],
                    ['COD_DRISTRI', 'character varying', 80],
                    ['NOM_DRISTRI', 'character varying', 80],
                    ['CAPITALES', 'character varying', 150],
                    ['COD_POSTAL', 'character varying', 6],
                    ['MARCA', 'character varying', 5],
                    ['FECHA', 'character varying', 10],
                    ['VERSION', 'character varying', 5],
                    ['GEOM', 'USER-DEFINED', np.nan]
                ]
                columnas_estr = pd.DataFrame(data, columns = ['column_name', 'dt_estr', 'lon_estr'])
                columnas_estr['column_name'] = columnas_estr['column_name'].apply(lambda x: x.lower())
                #--------------------NOMVIAs--------------------
                col_psql=set(columnas_psql['column_name'])
                col_estr=set(columnas_estr['column_name'])
                col_sobran = col_psql - col_estr-{'id'}
                col_faltan = col_estr - col_psql

                #-----------------Tipos$longitud-----------------
                result = pd.merge(columnas_estr, columnas_psql, on=['column_name'], how='outer')
                result = result[result['column_name'].isin(list(col_psql & col_estr-{'geom'}))]
                result['=tipo'] = result['dt_estr'] == result['dt_psql']
                result['=lon'] = result['lon_estr'] == result['lon_psql']
                dif_tipo = result[result['=tipo'] == False][['column_name']]['column_name'].tolist()
                dif_lon = result[result['=lon'] == False][['column_name']]['column_name'].tolist()
                
                capas.append(capa)         
                NOMVTOTAL_sobran.append(col_sobran)
                NOMVTOTAL_faltan.append(col_faltan)
                NOMVTOTAL_tipo.append(dif_tipo)
                NOMVTOTAL_lon.append(dif_lon)

            else:
            
                print('Error en la capa ingresada')
        
    elif 'brasil' in bd.lower():
        print('Brasil no cuenta con analisis de Estructura')
        capas = ['Brasil no cuenta con analisis de Estructura']
        NOMVTOTAL_sobran = ['']
        NOMVTOTAL_faltan = ['']
        NOMVTOTAL_tipo = ['']
        NOMVTOTAL_lon = ['']
        
    elif 'mexico' in bd.lower():
        print('Mexico no cuenta con analisis de Estructura')
        capas = ['Mexico no cuenta con analisis de Estructura']
        NOMVTOTAL_sobran = ['']
        NOMVTOTAL_faltan = ['']
        NOMVTOTAL_tipo = ['']
        NOMVTOTAL_lon = ['']
    elif 'ecuador' in bd.lower():
        print('Ecuador no cuenta con analisis de Estructura')
        capas = ['Ecuador no cuenta con analisis de Estructura']
        NOMVTOTAL_sobran = ['']
        NOMVTOTAL_faltan = ['']
        NOMVTOTAL_tipo = ['']
        NOMVTOTAL_lon = ['']
    elif 'salvador' in bd.lower():
        print('El Salvador no cuenta con analisis de Estructura')
        capas = ['El Salvador no cuenta con analisis de Estructura']
        NOMVTOTAL_sobran = ['']
        NOMVTOTAL_faltan = ['']
        NOMVTOTAL_tipo = ['']
        NOMVTOTAL_lon = ['']
    elif 'guatemala' in bd.lower():
        print('Guatemala no cuenta con analisis de Estructura')
        capas = ['Guatemala no cuenta con analisis de Estructura']
        NOMVTOTAL_sobran = ['']
        NOMVTOTAL_faltan = ['']
        NOMVTOTAL_tipo = ['']
        NOMVTOTAL_lon = ['']
    elif 'chile' in bd.lower():
        print('Chile no cuenta con analisis de Estructura')
        capas = ['Chile no cuenta con analisis de Estructura']
        NOMVTOTAL_sobran = ['']
        NOMVTOTAL_faltan = ['']
        NOMVTOTAL_tipo = ['']
        NOMVTOTAL_lon = ['']
    elif 'argentina' in bd.lower():
        print('Argentina no cuenta con analisis de Estructura')
        capas = ['Argentina no cuenta con analisis de Estructura']
        NOMVTOTAL_sobran = ['']
        NOMVTOTAL_faltan = ['']
        NOMVTOTAL_tipo = ['']
        NOMVTOTAL_lon = ['']
    elif 'panama' in bd.lower():
        print('Panama no cuenta con analisis de Estructura')
        capas = ['Panama no cuenta con analisis de Estructura']
        NOMVTOTAL_sobran = ['']
        NOMVTOTAL_faltan = ['']
        NOMVTOTAL_tipo = ['']
        NOMVTOTAL_lon = ['']
    elif 'honduras' in bd.lower():
        print('Honduras no cuenta con analisis de Estructura')
        capas = ['Honduras no cuenta con analisis de Estructura']
        NOMVTOTAL_sobran = ['']
        NOMVTOTAL_faltan = ['']
        NOMVTOTAL_tipo = ['']
        NOMVTOTAL_lon = ['']    
    return capas, NOMVTOTAL_sobran, NOMVTOTAL_faltan, NOMVTOTAL_tipo, NOMVTOTAL_lon
