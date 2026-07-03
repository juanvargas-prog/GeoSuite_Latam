import os
import geopandas as gpd
from sqlalchemy import create_engine
import fiona

def Brasil_QueryExpCapa(engine,tabla,carpeta_final):
  
    if tabla[0:3] == 'cep':
    
        print(tabla.upper())
    
        shapefile_name = "cep"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "cod_estado":"VARCHAR(10)",
            "nom_estado":"VARCHAR(100)",
            "cod_mun":"VARCHAR(10)",
            "nom_mun":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa":'int',
                    "cod_estado":'str:10',
                    "nom_estado":'str:100',
                    "cod_mun":'str:10',
                    "nom_mun":'str:100',
                    "marca":'str:5',
                    "fecha":'str:10',
                    "version":'str:5'
                }
            }
            
    elif tabla[0:13] == 'concentracion':   
    
        print(tabla.upper())
    
        shapefile_name = "concentração_urbana"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "cod_fvla":"VARCHAR(10)",
            "nom_fvla":"VARCHAR(100)",
            "cod_estado":"VARCHAR(10)",
            "nom_estado":"VARCHAR(100)",
            "cod_mun":"VARCHAR(10)",
            "nom_mun":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "observ":"VARCHAR(30)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa":'int',
                    "cod_fvla":'str:10',
                    "nom_fvla":'str:100',
                    "cod_estado":'str:10',
                    "nom_estado":'str:100',
                    "cod_mun":'str:10',
                    "nom_mun":'str:100',
                    "cod_distri":'str:10',
                    "nom_distri":'str:100',
                    "observ":'str:30',
                    "marca":'str:5',
                    "fecha":'str:10',
                    "version":'str:5'
                }
            }

    elif tabla[0:8] == 'distrito':
        #print('si entre')
        print(tabla.upper())

        shapefile_name = "distrito"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "cod_estado":"VARCHAR(10)",
            "nom_estado":"VARCHAR(100)",
            "cod_mun":"VARCHAR(10)",
            "nom_mun":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "observ":"VARCHAR(30)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        
        schema = {
                'geometry': 'Unknown',  
                'properties': {
                    "id_capa":'int',
                    "cod_estado":'str:10',
                    "nom_estado":'str:100',
                    "cod_mun":'str:10',
                    "nom_mun":'str:100',
                    "cod_distri":'str:10',
                    "nom_distri":'str:100',
                    "observ":'str:30',
                    "marca":'str:5',
                    "fecha":'str:10',
                    "version":'str:5'
                }
            }

            
    elif tabla[0:6] == 'estado':
        #print('si entre')
        print(tabla.upper())

        shapefile_name = "estado"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "cod_estado":"VARCHAR(10)",
            "nom_estado":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
            'geometry': 'Unknown',  
            'properties': {
                "id_capa":'int',
                "cod_estado":'str:10',
                "nom_estado":'str:100',
                "marca":'str:5',
                "fecha":'str:10',
                "version":'str:5'
            }
        }

            
    elif tabla[0:6] == 'barrio':
    
        print(tabla.upper())    
        
        shapefile_name = "bairro"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "tipo_barrio":"VARCHAR(80)",
            "cod_bar":"VARCHAR(10)",
            "nom_bar":"VARCHAR(100)",
            "cod_estado":"VARCHAR(10)",
            "nom_estado":"VARCHAR(100)",
            "cod_mun":"VARCHAR(10)",
            "nom_mun":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "observ":"VARCHAR(30)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }

        schema = {
            'geometry': 'Unknown',  
            'properties': {
                "id_capa":'int',
                "tipo_barrio":'str:80',
                "cod_bar":'str:10',
                "nom_bar":'str:100',   
                "cod_estado":'str:10',
                "nom_estado":'str:100',
                "cod_mun":'str:10',
                "nom_mun":'str:100',
                "cod_distri":'str:10',
                "nom_distri":'str:100',
                "observ":'str:30',
                "marca":'str:5',
                "fecha":'str:10',
                "version":'str:5'
            }
        }
            
    elif tabla[0:11] == 'hidrografia':
        print(tabla.upper())
        
        shapefile_name = "hidrografia"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "nombre":"VARCHAR(100)",
            "cod_estado":"VARCHAR(10)",
            "nom_estado":"VARCHAR(100)",
            "cod_mun":"VARCHAR(10)",
            "nom_mun":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }

        schema = {
            'geometry': 'Unknown',  
            'properties': {
                "id_capa":'int',
                "nombre":'str:100',   
                "cod_estado":'str:10',
                "nom_estado":'str:100',
                "cod_mun":'str:10',
                "nom_mun":'str:100',
                "cod_distri":'str:10',
                "nom_distri":'str:100',
                "marca":'str:5',
                "fecha":'str:10',
                "version":'str:5'
            }
        }
            
    elif tabla[0:7] == 'manzana':
    
        print(tabla.upper())
        
        shapefile_name = "maçã"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "cod_mz":"VARCHAR(30)",
            "manzana":"VARCHAR(100)",
            "nse":"VARCHAR(5)",
            "cod_postal":"VARCHAR(10)",
            "cod_estado":"VARCHAR(10)",
            "nom_estado":"VARCHAR(100)",
            "cod_mun":"VARCHAR(10)",
            "nom_mun":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "cod_bar":"VARCHAR(10)",
            "nom_bar":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }

        schema = {
            'geometry': 'Unknown',  
            'properties': {
                "id_capa":'int',
                "cod_mz":'str:30',
                "manzana":'str:100',
                "nse":'str:5',
                "cod_postal":'str:10',
                "cod_estado":'str:10',
                "nom_estado":'str:100',
                "cod_mun":'str:10',
                "nom_mun":'str:100',
                "cod_distri":'str:10',
                "nom_distri":'str:100',
                "cod_bar":'str:10',
                "nom_bar":'str:100', 
                "marca":'str:5',
                "fecha":'str:10',
                "version":'str:5'
            }
        }
        
    elif tabla[0:7] == 'mavvial':  
    
        print(tabla.upper())    
        
        shapefile_name = "experiente"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "tipovia":"VARCHAR(10)",
            "nomvia":"VARCHAR(100)",
            "nomvtotal":"VARCHAR(100)",
            "generadora":"VARCHAR(50)",
            "entre_via":"VARCHAR(100)",
            "costado":"VARCHAR(1)",
            "rango_par":"VARCHAR(20)",
            "rango_imp":"VARCHAR(20)",
            "cod_postal":"VARCHAR(10)",
            "categ_vial":"VARCHAR(10)",
            "oneway":"VARCHAR(2)",
            "velocidad":"VARCHAR(3)",
            "marca_vial":"VARCHAR(10)",
            "cod_estado":"VARCHAR(10)",
            "nom_estado":"VARCHAR(100)",
            "cod_mun":"VARCHAR(10)",
            "nom_mun":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }

        
    elif tabla[0:6] == 'parque':
    
        print(tabla.upper())
    
        shapefile_name = "parque_e_área_verde"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "nombre":"VARCHAR(100)",
            "cod_estado":"VARCHAR(10)",
            "nom_estado":"VARCHAR(100)",
            "cod_mun":"VARCHAR(10)",
            "nom_mun":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        
        schema = {
            'geometry': 'Unknown',
            'properties': {
                "id_capa": 'int',
                "nombre": 'str:100',
                "cod_estado": 'str:10',
                "nom_estado": 'str:100',
                "cod_mun": 'str:10',
                "nom_mun": 'str:100',
                "cod_distri": 'str:10',
                "nom_distri": 'str:100',
                "marca": 'str:5',
                "fecha": 'str:10',
                "version": 'str:5'
            }
        }
    
    elif tabla[0:5] == 'placa':
    
        print(tabla.upper())
    
        shapefile_name = "placa"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "tipovia":"VARCHAR(10)",
            "nomvia":"VARCHAR(100)",
            "nomvtotal":"VARCHAR(100)",
            "generadora":"VARCHAR(50)",
            "placa":"VARCHAR(10)",
            "manzana":"VARCHAR(30)",
            "casa_lote":"VARCHAR(50)",
            "tipo_dir":"VARCHAR(20)",
            "direccion":"VARCHAR(180)",
            "cod_postal":"VARCHAR(10)",
            "id_predio":"INTEGER",
            "id_mavvial":"INTEGER",
            "cod_estado":"VARCHAR(10)",
            "nom_estado":"VARCHAR(100)",
            "cod_mun":"VARCHAR(10)",
            "nom_mun":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "observ_dat":"VARCHAR(30)",
            "observ_pos":"VARCHAR(30)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
            'geometry': 'Unknown',
            'properties': {
                "id_capa": 'int',
                "tipovia": 'str:10',
                "nomvia": 'str:100',
                "nomvtotal": 'str:100',
                "generadora": 'str:50',
                "placa": 'str:10',
                "manzana": 'str:30',
                "casa_lote": 'str:50',
                "tipo_dir": 'str:20',
                "direccion": 'str:180',
                "cod_postal": 'str:10',
                "id_predio": 'int',
                "id_mavvial": 'int',
                "cod_estado": 'str:10',
                "nom_estado": 'str:100',
                "cod_mun": 'str:10',
                "nom_mun": 'str:100',
                "cod_distri": 'str:10',
                "nom_distri": 'str:100',
                "observ_dat": 'str:30',
                "observ_pos": 'str:30',
                "marca": 'str:5',
                "fecha": 'str:10',
                "version": 'str:5'
            }
        }
            
    else:
        print("No existe Estructura Para Exportar la Capa")
        return
    try:

        with engine.connect() as connection:
            # Preparar la consulta
            column_casts = ", ".join([f"CAST({col} AS {spec}) AS {col}" for col, spec in output_column_specs.items()])
            #print(column_casts)
            
            query = f"SELECT {column_casts} FROM {tabla};"
            #print(query)

            # Cargar los datos como un GeoDataFrame
            gdf = gpd.read_postgis(query, connection, geom_col="geom")

            # Exportar los datos como un Shapefile
            gdf.to_file(output_file,engine="fiona", driver="ESRI Shapefile", schema=schema)

            print(f"Shapefile exportado correctamente a {output_file}")

    except Exception as e:
        print(f"Error: {e}")

def Brasil_QueryExpGdb(engine,lista,carpeta_final):

    print(lista)

    for tabla in lista:
        
        exportar = False
        
        if tabla[0:3] == 'cep':

            print(tabla.upper())
        
            shapefile_name = "cep"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "cod_estado":"VARCHAR(10)",
                "nom_estado":"VARCHAR(100)",
                "cod_mun":"VARCHAR(10)",
                "nom_mun":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                    'geometry': 'Unknown',
                    'properties': {
                        "id_capa":'int',
                        "cod_estado":'str:10',
                        "nom_estado":'str:100',
                        "cod_mun":'str:10',
                        "nom_mun":'str:100',
                        "marca":'str:5',
                        "fecha":'str:10',
                        "version":'str:5'
                    }
                }
            
            exportar = True
                
        elif tabla[0:13] == 'concentracion':   
        
            print(tabla.upper())
        
            shapefile_name = "concentração_urbana"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "cod_fvla":"VARCHAR(10)",
                "nom_fvla":"VARCHAR(100)",
                "cod_estado":"VARCHAR(10)",
                "nom_estado":"VARCHAR(100)",
                "cod_mun":"VARCHAR(10)",
                "nom_mun":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "observ":"VARCHAR(30)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                    'geometry': 'Unknown',
                    'properties': {
                        "id_capa":'int',
                        "cod_fvla":'str:10',
                        "nom_fvla":'str:100',
                        "cod_estado":'str:10',
                        "nom_estado":'str:100',
                        "cod_mun":'str:10',
                        "nom_mun":'str:100',
                        "cod_distri":'str:10',
                        "nom_distri":'str:100',
                        "observ":'str:30',
                        "marca":'str:5',
                        "fecha":'str:10',
                        "version":'str:5'
                    }
                }
                            
            exportar = True

        elif tabla[0:8] == 'distrito':
            #print('si entre')
            print(tabla.upper())

            shapefile_name = "distrito"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "cod_estado":"VARCHAR(10)",
                "nom_estado":"VARCHAR(100)",
                "cod_mun":"VARCHAR(10)",
                "nom_mun":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "observ":"VARCHAR(30)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            
            schema = {
                    'geometry': 'Unknown',  
                    'properties': {
                        "id_capa":'int',
                        "cod_estado":'str:10',
                        "nom_estado":'str:100',
                        "cod_mun":'str:10',
                        "nom_mun":'str:100',
                        "cod_distri":'str:10',
                        "nom_distri":'str:100',
                        "observ":'str:30',
                        "marca":'str:5',
                        "fecha":'str:10',
                        "version":'str:5'
                    }
                }
                            
            exportar = True

                
        elif tabla[0:6] == 'estado':
            #print('si entre')
            print(tabla.upper())

            shapefile_name = "estado"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "cod_estado":"VARCHAR(10)",
                "nom_estado":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                'geometry': 'Unknown',  
                'properties': {
                    "id_capa":'int',
                    "cod_estado":'str:10',
                    "nom_estado":'str:100',
                    "marca":'str:5',
                    "fecha":'str:10',
                    "version":'str:5'
                }
            }  
            
            exportar = True

                
        elif tabla[0:6] == 'barrio':
        
            print(tabla.upper())    
            
            shapefile_name = "bairro"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "tipo_barrio":"VARCHAR(80)",
                "cod_bar":"VARCHAR(10)",
                "nom_bar":"VARCHAR(100)",
                "cod_estado":"VARCHAR(10)",
                "nom_estado":"VARCHAR(100)",
                "cod_mun":"VARCHAR(10)",
                "nom_mun":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "observ":"VARCHAR(30)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }

            schema = {
                'geometry': 'Unknown',  
                'properties': {
                    "id_capa":'int',
                    "tipo_barrio":'str:80',
                    "cod_bar":'str:10',
                    "nom_bar":'str:100',   
                    "cod_estado":'str:10',
                    "nom_estado":'str:100',
                    "cod_mun":'str:10',
                    "nom_mun":'str:100',
                    "cod_distri":'str:10',
                    "nom_distri":'str:100',
                    "observ":'str:30',
                    "marca":'str:5',
                    "fecha":'str:10',
                    "version":'str:5'
                }
            }
             
                         
            exportar = True
        elif tabla[0:11] == 'hidrografia':
            print(tabla.upper())
            
            shapefile_name = "hidrografia"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "nombre":"VARCHAR(100)",
                "cod_estado":"VARCHAR(10)",
                "nom_estado":"VARCHAR(100)",
                "cod_mun":"VARCHAR(10)",
                "nom_mun":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }

            schema = {
                'geometry': 'Unknown',  
                'properties': {
                    "id_capa":'int',
                    "nombre":'str:100',   
                    "cod_estado":'str:10',
                    "nom_estado":'str:100',
                    "cod_mun":'str:10',
                    "nom_mun":'str:100',
                    "cod_distri":'str:10',
                    "nom_distri":'str:100',
                    "marca":'str:5',
                    "fecha":'str:10',
                    "version":'str:5'
                }
            }
                
                         
            exportar = True
            
        elif tabla[0:7] == 'manzana':
        
            print(tabla.upper())
            
            shapefile_name = "maçã"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "cod_mz":"VARCHAR(30)",
                "manzana":"VARCHAR(100)",
                "nse":"VARCHAR(5)",
                "cod_postal":"VARCHAR(10)",
                "cod_estado":"VARCHAR(10)",
                "nom_estado":"VARCHAR(100)",
                "cod_mun":"VARCHAR(10)",
                "nom_mun":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "cod_bar":"VARCHAR(10)",
                "nom_bar":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }

            schema = {
                'geometry': 'Unknown',  
                'properties': {
                    "id_capa":'int',
                    "cod_mz":'str:30',
                    "manzana":'str:100',
                    "nse":'str:5',
                    "cod_postal":'str:10',
                    "cod_estado":'str:10',
                    "nom_estado":'str:100',
                    "cod_mun":'str:10',
                    "nom_mun":'str:100',
                    "cod_distri":'str:10',
                    "nom_distri":'str:100',
                    "cod_bar":'str:10',
                    "nom_bar":'str:100', 
                    "marca":'str:5',
                    "fecha":'str:10',
                    "version":'str:5'
                }
            }
            
                        
            exportar = True
            
        elif tabla[0:7] == 'mavvial':  
        
            print(tabla.upper())    
            
            shapefile_name = "experiente"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "tipovia":"VARCHAR(10)",
                "nomvia":"VARCHAR(100)",
                "nomvtotal":"VARCHAR(100)",
                "generadora":"VARCHAR(50)",
                "entre_via":"VARCHAR(100)",
                "costado":"VARCHAR(1)",
                "rango_par":"VARCHAR(20)",
                "rango_imp":"VARCHAR(20)",
                "cod_postal":"VARCHAR(10)",
                "categ_vial":"VARCHAR(10)",
                "oneway":"VARCHAR(2)",
                "velocidad":"VARCHAR(3)",
                "marca_vial":"VARCHAR(10)",
                "cod_estado":"VARCHAR(10)",
                "nom_estado":"VARCHAR(100)",
                "cod_mun":"VARCHAR(10)",
                "nom_mun":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa": 'int',
                    "tipovia": 'str:10',
                    "nomvia": 'str:100',
                    "nomvtotal": 'str:100',
                    "generadora": 'str:50',
                    "entre_via": 'str:100',
                    "costado": 'str:1',
                    "rango_par": 'str:20',
                    "rango_imp": 'str:20',
                    "cod_postal": 'str:10',
                    "categ_vial": 'str:10',
                    "oneway": 'str:2',
                    "velocidad": 'str:3',
                    "marca_vial": 'str:10',
                    "cod_estado": 'str:10',
                    "nom_estado": 'str:100',
                    "cod_mun": 'str:10',
                    "nom_mun": 'str:100',
                    "cod_distri": 'str:10',
                    "nom_distri": 'str:100',
                    "marca": 'str:5',
                    "fecha": 'str:10',
                    "version": 'str:5'
                }
            }
            
            exportar = True
            
        elif tabla[0:6] == 'parque':
        
            print(tabla.upper())
        
            shapefile_name = "parque_e_área_verde"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "nombre":"VARCHAR(100)",
                "cod_estado":"VARCHAR(10)",
                "nom_estado":"VARCHAR(100)",
                "cod_mun":"VARCHAR(10)",
                "nom_mun":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            
            schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa": 'int',
                    "nombre": 'str:100',
                    "cod_estado": 'str:10',
                    "nom_estado": 'str:100',
                    "cod_mun": 'str:10',
                    "nom_mun": 'str:100',
                    "cod_distri": 'str:10',
                    "nom_distri": 'str:100',
                    "marca": 'str:5',
                    "fecha": 'str:10',
                    "version": 'str:5'
                }
            }
            exportar = True
        elif tabla[0:5] == 'placa':
        
            print(tabla.upper())
        
            shapefile_name = "placa"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "tipovia":"VARCHAR(10)",
                "nomvia":"VARCHAR(100)",
                "nomvtotal":"VARCHAR(100)",
                "generadora":"VARCHAR(50)",
                "placa":"VARCHAR(10)",
                "manzana":"VARCHAR(30)",
                "casa_lote":"VARCHAR(50)",
                "tipo_dir":"VARCHAR(20)",
                "direccion":"VARCHAR(180)",
                "cod_postal":"VARCHAR(10)",
                "id_predio":"INTEGER",
                "id_mavvial":"INTEGER",
                "cod_estado":"VARCHAR(10)",
                "nom_estado":"VARCHAR(100)",
                "cod_mun":"VARCHAR(10)",
                "nom_mun":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "observ_dat":"VARCHAR(30)",
                "observ_pos":"VARCHAR(30)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa": 'int',
                    "tipovia": 'str:10',
                    "nomvia": 'str:100',
                    "nomvtotal": 'str:100',
                    "generadora": 'str:50',
                    "placa": 'str:10',
                    "manzana": 'str:30',
                    "casa_lote": 'str:50',
                    "tipo_dir": 'str:20',
                    "direccion": 'str:180',
                    "cod_postal": 'str:10',
                    "id_predio": 'int',
                    "id_mavvial": 'int',
                    "cod_estado": 'str:10',
                    "nom_estado": 'str:100',
                    "cod_mun": 'str:10',
                    "nom_mun": 'str:100',
                    "cod_distri": 'str:10',
                    "nom_distri": 'str:100',
                    "observ_dat": 'str:30',
                    "observ_pos": 'str:30',
                    "marca": 'str:5',
                    "fecha": 'str:10',
                    "version": 'str:5'
                }
            }
            exportar = True 
        else:
            print("No existe Estructura Para Exportar la Capa")

        if exportar:
            try:

                with engine.connect() as connection:
                    # Preparar la consulta
                    column_casts = ", ".join([f"CAST({col} AS {spec}) AS {col}" for col, spec in output_column_specs.items()])
                    #print(column_casts)
                    
                    query = f"SELECT {column_casts} FROM {tabla};"
                    #print(query)

                    # Cargar los datos como un GeoDataFrame
                    gdf = gpd.read_postgis(query, connection, geom_col="geom")

                    # Exportar los datos como un Shapefile
                    gdf.to_file(output_file,engine="fiona", driver="ESRI Shapefile", schema=schema)

                    print(f"Shapefile exportado correctamente a {output_file}")

            except Exception as e:
                print(f"Error: {e}")