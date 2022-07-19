from colorama import Cursor
from flask import Flask
from flask import render_template, request, redirect, url_for, send_from_directory
from flaskext.mysql import MySQL
from datetime import datetime
import os

app= Flask(__name__)
mysql= MySQL()

app.config['MYSQL_DATABASE_HOST']= 'localhost'
app.config['MYSQL_DATABASE_USER']= 'root'
app.config['MYSQL_DATABASE_PASSWORD']= 'root'
app.config['MYSQL_DATABASE_DB']= 'empleados'

UPLOADS = os.path.join('uploads') #('src/uploads')
app.config['UPLOADS'] = UPLOADS # guardamos la ruta como un valor en la app

mysql.init_app(app)


@app.route('/fotodeusuario/<path:nombreFoto>') # esto sirve para ocultar donde tengo mis fotos. el navegador mapea esto y le da al usuario esta dire y no la real.
def uploads(nombreFoto):
    return send_from_directory(os.path.join('uploads'), nombreFoto)

@app.route('/') # define una ruta de acceso
def index():
    conn=mysql.connect()
    cursor = conn.cursor()

    sql= "SELECT * FROM `empleados`.`empleados`;"
    cursor.execute(sql)
    
    empleados = cursor.fetchall()

    conn.commit()

    return render_template('empleados/index.html', empleados=empleados)

@app.route('/create') # por defecto viene el method GET: ('/create', methods=['GET'])
def create():
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre'] # lo recibe del form
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto'] # lo recibe como archivo, un stream de datos

    now = datetime.now()
    print(now)
    tiempo = now.strftime("%Y%H%M%S")
    print(tiempo)

    if _foto.filename != '':
        nuevoNombreFoto = tiempo + '_' + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto) # "src/uploads/"

    
    sql= "INSERT INTO  `empleados`.`empleados` (nombre, correo, foto) VALUES (%s,%s,%s);" # no debo usar format strings (f'algo "{dato}" algo') porque esto permite inyectar codigo malicioso en la BD "inyeccion SQL"
    datos= (_nombre,_correo,nuevoNombreFoto)

    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

    return redirect('/')


@app.route('/modify/<int:id>')
def modify(id):
    sql = 'SELECT * FROM `empleados`.`empleados` WHERE id=%s;'
    conn = mysql.connect()
    cursor= conn.cursor()
    cursor.execute(sql,id)
    empleado= cursor.fetchone()
    conn.commit()

    return render_template('empleados/edit.html', empleado = empleado)

@app.route('/update', methods=['POST'])
def update():
    _nombre= request.form['txtNombre']
    _correo= request.form['txtCorreo']
    _foto= request.files['txtFoto']
    id= request.form['txtId']

    # datos = (_nombre, _correo, id) # old school

    conn= mysql.connect()
    cursor= conn.cursor()

    if _foto.filename != '':
        now = datetime.now()
        tiempo= now.strftime("%Y%H%M%S")
        nuevoNombreFoto = tiempo + '_' + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto) # "src/uploads/"
    
        sql= 'SELECT foto FROM `empleados`.`empleados` WHERE id=%s;'
        cursor.execute(sql,id)
        conn.commit()

        nombreFoto = cursor.fetchone()[0] # esto esta muy feo
        borrarEstaFoto = os.path.join(app.config['UPLOADS'], nombreFoto) # esto no se para que lo hace, para mi que se equivocó y esto va abajo
        print(borrarEstaFoto)

        try:
            os.remove(os.path.join(app.config['UPLOADS'], nombreFoto)) # para mi aca va borrarEstaFoto en lugar de nombreFoto
        except:
            pass

        sql = 'UPDATE `empleados`.`empleados` SET foto=%s WHERE id=%s;'
        datos= (nuevoNombreFoto,id)
        cursor.execute(sql, datos)
        conn.commit()
        
    sql = 'UPDATE `empleados`.`empleados` SET nombre=%s, correo=%s WHERE id=%s;'
    datos = (_nombre,_correo,id)
    cursor.execute(sql,datos)
    conn.commit()

    return redirect('/')

@app.route('/delete/<int:id>') # lo que está entre <> es un parámetro.
def delete(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = 'SELECT foto from `empleados`.`empleados` WHERE id=%s;'
    cursor.execute(sql,id)

    nombreFoto = cursor.fetchone()[0] # le pongo 0 para desestructurar y que me de el objeto 1 de la tupla

    try:
        os.remove(os.path.join(app.config['UPLOADS'], nombreFoto))
    except:
        pass

    sql = 'DELETE FROM `empleados`.`empleados` WHERE id=%s;'
    cursor.execute(sql,id) 
    
    conn.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)