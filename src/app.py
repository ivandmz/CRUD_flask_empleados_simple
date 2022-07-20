from flask import Flask
from flask import render_template, request, redirect, url_for, send_from_directory
from pymysql.cursors import DictCursor
from flaskext.mysql import MySQL
from datetime import datetime
import os

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'empleados'

UPLOADS = os.path.join('uploads')  # ('src/uploads')
app.config['UPLOADS'] = UPLOADS  # guardamos la ruta como un valor en la app

mysql.init_app(app)

# como tengo estos aca arriba puedo borrar los de los metodos debajo. (pero solo los voy a comentar)
conn = mysql.connect()
cursor = conn.cursor(cursor=DictCursor) # me trae los datos de la DB como dict {clave:valor} {'id':'1','nombre':'ivan',...}


def queryMySql(query, data=None, tipoDeRetorno='none'):
    if data != None:
        cursor.execute(query, data)
    else:
        cursor.execute(query)

    if tipoDeRetorno == "one":
        registro = cursor.fetchone()
    else:
        registro = cursor.fetchall()
    if query.casefold().find("select") != -1: #casefold convierte todo el sql en minusculas, y find busca si en el query esta select
        conn.commit() # entonces commitea
    return registro # siempre devuelve algo, a veces vacio (select) a veces se pierde (si no lo guardo en una var)


# esto sirve para ocultar donde tengo mis fotos. el navegador mapea esto y le da al usuario esta dire y no la real.
@app.route('/fotodeusuario/<path:nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(os.path.join('uploads'), nombreFoto)


@app.route('/')  # define una ruta de acceso
def index():

    sql = "SELECT * FROM `empleados`.`empleados`;"
    empleados = queryMySql(sql, None, "all")
    print(empleados)

    return render_template('empleados/index.html', empleados=empleados)


# por defecto viene el method GET: ('/create', methods=['GET'])
@app.route('/empleado/crear', methods=['GET','POST'])
def alta_empleado():
    if request.method == "GET":
        return render_template('empleados/create.html') # no es buena practica enviar returns dentro! pero el profe no lo explicó
    elif request.method == "POST":
        _nombre = request.form['txtNombre']  # lo recibe del form
        _correo = request.form['txtCorreo']
        _foto = request.files['txtFoto']# lo recibe como archivo, un stream de datos

        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")

        if _foto.filename != '':
            nuevoNombreFoto = tiempo + '_' + _foto.filename
            _foto.save("uploads/" + nuevoNombreFoto)  # "src/uploads/"

        # no debo usar format strings (f'algo "{dato}" algo') porque esto permite inyectar codigo malicioso en la BD "inyeccion SQL"
        sql = "INSERT INTO  `empleados`.`empleados` (nombre, correo, foto) VALUES (%s,%s,%s);"
        datos = (_nombre, _correo, nuevoNombreFoto)

        queryMySql(sql, datos)  # con esta fn nos ahorramos todo el codigo de abajo

        return redirect('/')


# @app.route('/modify/<int:id>')
# def modify(id):
#     sql = 'SELECT * FROM `empleados`.`empleados` WHERE id=%s;'
#     datos = [id]
#     empleado = queryMySql(sql, datos, "one")

#     return render_template('empleados/edit.html', empleado=empleado)


# @app.route('/update', methods=['POST'])
# def update():
#     _nombre = request.form['txtNombre']
#     _correo = request.form['txtCorreo']
#     _foto = request.files['txtFoto']
#     id = request.form['txtId']

#     if _foto.filename != '':
#         now = datetime.now()
#         tiempo = now.strftime("%Y%H%M%S")
#         nuevoNombreFoto = tiempo + '_' + _foto.filename
#         _foto.save("uploads/" + nuevoNombreFoto)  # "src/uploads/"

#         sql = 'SELECT foto FROM `empleados`.`empleados` WHERE id=%s;'
#         datos = [id]
#         nombreFoto = queryMySql(sql, datos, "one")
#         print(nombreFoto)

#         try:
#             # para mi aca va borrarEstaFoto en lugar de nombreFoto
#             os.remove(os.path.join(app.config['UPLOADS'], nombreFoto['foto']))
#         except:
#             print('-------------------')
#             print('Error al intentar borrar la foto.')
#             pass

#         sql = 'UPDATE `empleados`.`empleados` SET foto=%s WHERE id=%s;'
#         datos = (nuevoNombreFoto, id)
#         queryMySql(sql, datos)

#     sql = 'UPDATE `empleados`.`empleados` SET nombre=%s, correo=%s WHERE id=%s;'
#     datos = (_nombre, _correo, id)
#     queryMySql(sql, datos)

#     return redirect('/')

@app.route('/empleado/modificar/<int:id>', methods=['GET','POST'])
def modif_empleado(id):
    if request.method == "GET":
        sql = 'SELECT * FROM `empleados`.`empleados` WHERE id=%s;'
        datos = [id]
        empleado = queryMySql(sql, datos, "one")

        return render_template('empleados/edit.html', empleado=empleado)

    elif request.method == "POST":
        _nombre = request.form['txtNombre']
        _correo = request.form['txtCorreo']
        _foto = request.files['txtFoto']
        id = request.form['txtId']

        if _foto.filename != '':
            now = datetime.now()
            tiempo = now.strftime("%Y%H%M%S")
            nuevoNombreFoto = tiempo + '_' + _foto.filename
            _foto.save("uploads/" + nuevoNombreFoto)  # "src/uploads/"

            sql = 'SELECT foto FROM `empleados`.`empleados` WHERE id=%s;'
            datos = [id]
            nombreFoto = queryMySql(sql, datos, "one")
            print(nombreFoto)

            try:
                # para mi aca va borrarEstaFoto en lugar de nombreFoto
                os.remove(os.path.join(app.config['UPLOADS'], nombreFoto['foto']))
            except:
                print('-------------------')
                print('Error al intentar borrar la foto.')
                pass

            sql = 'UPDATE `empleados`.`empleados` SET foto=%s WHERE id=%s;'
            datos = (nuevoNombreFoto, id)
            queryMySql(sql, datos)

        sql = 'UPDATE `empleados`.`empleados` SET nombre=%s, correo=%s WHERE id=%s;'
        datos = (_nombre, _correo, id)
        queryMySql(sql, datos)

        return redirect('/')


@app.route('/empleado/delete/<int:id>')  # lo que está entre <> es un parámetro.
def baja_empleado(id): # lo correcto sería: en lugar de borrar, tener un casillero en la DB alta/baja. para no borrar y perder los datos.

    sql = 'SELECT foto from `empleados`.`empleados` WHERE id=%s;'
    datos = [id]

    nombreFoto = queryMySql(sql, datos, "one")

    try:
        os.remove(os.path.join(app.config['UPLOADS'], nombreFoto['foto']))
    except:
        print('-------------------')
        print('Error al intentar borrar la foto.')
        pass

    sql = 'DELETE FROM `empleados`.`empleados` WHERE id=%s;'
    queryMySql(sql,datos)

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)