from isa import app
from flask import Flask, render_template, request, flash, session, redirect, url_for
from forms import SignupForm, SigninForm, AddRestaurante, EditRestaurant
from models import db, User, friend_request, Friends, Restaurant, RestaurantManager
from sqlalchemy import or_, and_, not_

@app.route('/')
def home():
	if 'email' not in session:
		user = None
	else:
		user = User.query.filter_by(email = session['email']).first()

	return render_template('home.html', user=user)



@app.route('/testdb')
def testdb():
	if db.session.query("1").from_statement("SELECT 1").all():
		return 'It works.'
	else:
		return 'Something is broken.'



@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignupForm()

	if 'email' in session:
		return redirect(url_for('profile'))
   
	if request.method == 'POST':
		if form.validate() == False:
			return render_template('signup.html', form=form)
		else:   
			newuser = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data, "user", 0)
			db.session.add(newuser)
			db.session.commit()

			session['email'] = newuser.email
			session['role'] = newuser.role
			
			return redirect(url_for('profile'))

	elif request.method == 'GET':
		return render_template('signup.html', form=form)




@app.route('/signin', methods=['GET', 'POST'])
def signin():
	form = SigninForm()
   
	if 'email' in session:
		return redirect(url_for('profile'))

	if request.method == 'POST':
		if form.validate() == False:
			return render_template('signin.html', form=form)
		else:
			session['email'] = form.email.data
			return redirect(url_for('profile'))
                 
	elif request.method == 'GET':
		return render_template('signin.html', form=form)



@app.route('/signout')
def signout():
 
	if 'email' not in session:
		return redirect(url_for('signin'))
     
	session.pop('email', None)
	return redirect(url_for('home'))




@app.route('/profile')
def profile():
 
	if 'email' not in session:
		return redirect(url_for('signin'))
 
	user = User.query.filter_by(email = session['email']).first()
 
	if user is None:
		return redirect(url_for('signin'))
	else:
		return render_template('profile.html', user=user)



@app.route('/friends', methods=['GET', 'POST'])
def friends():

	user = User.query.filter_by(email = session['email']).first()
	active_user = user.id

	friendsList = Friends.query.filter(or_(Friends.user_one == active_user, Friends.user_two == active_user)).all()
	fList = []
	for f in friendsList:
		if f.user_one == active_user:
			fList.append(f.user_two)
		else:
			fList.append(f.user_one)

	friends = User.query.filter(User.id.in_(fList)).all()


	requestsList = friend_request.query.filter_by(to_id = active_user).all()
	reqList = []
	for r in requestsList:
		reqList.append(r.from_id)

	requests = User.query.filter(User.id.in_(reqList)).all()

	return render_template('friends.html', friends=friends, requests=requests, user=user)


@app.route('/restaurants', methods=['GET', 'POST'])
def restaurants():
	user = User.query.filter_by(email = session['email']).first()
	restorants = Restaurant.query.all()

	return render_template('restaurants.html', user=user, restaurants=restorants)
	

@app.route('/filter_restaurants', methods=['GET', 'POST'])
def filter_restaurants():
	user = User.query.filter_by(email = session['email']).first()

	if request.method == "POST":
		naziv = request.form['naziv']
		tip = request.form['tip']

		if naziv and tip:
			restorants = Restaurant.query.filter(and_(Restaurant.name == naziv, Restaurant.type == tip)).all()
			print 'OBA'
		elif not naziv and not tip:
			restorants = Restaurant.query.all()
		elif not naziv:
			restorants = Restaurant.query.filter(Restaurant.type == tip)
			print 'TIP'
		elif not tip:
			print 'NAZIV'
			restorants = Restaurant.query.filter(Restaurant.name == naziv)
		
		return render_template('restaurants.html', user=user, restaurants=restorants)
	else:
		restorants = Restaurant.query.all()
		return render_template('restaurants.html', user=user, restaurants=restorants)
	



@app.route('/follow/<from_id>')
def follow(from_id):
	user = User.query.filter_by(email = session['email']).first()
	follow_from = user.id
	to_follow = from_id

	f_reg = friend_request(follow_from, to_follow)
	db.session.add(f_reg)
	db.session.commit()


	return redirect(url_for('friends'))



@app.route('/add_remove/<option>/<from_id>')
def add_remove(option, from_id):
	user = User.query.filter_by(email = session['email']).first()
	follow_from = user.id
	to_follow = from_id

	friend_request.query.filter(friend_request.from_id == to_follow, friend_request.to_id == follow_from).delete()
	db.session.commit()

	if option == 'dodaj':
		f = Friends(follow_from, to_follow)
		db.session.add(f)
		db.session.commit()
	elif option == 'obrisi':
		Friends.query.filter(or_(and_(Friends.user_one == follow_from, Friends.user_two == to_follow), and_(Friends.user_one == to_follow, Friends.user_two == follow_from))).delete()
		db.session.commit()


	return redirect(url_for('friends'))

 

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        search = request.form['search']
        words = search.split(' ')

        user = User.query.filter_by(email = session['email']).first()
        active_user = user.id

        search_result = User.query.filter(and_(or_(*[User.first_name.like(word + "%") for word in words]), User.id != active_user)).all()

        idList = []

        for i in search_result:
        	idList.append(i.id)

        friend_id = Friends.query.filter(or_(Friends.user_one.in_(idList), Friends.user_two.in_(idList)))

        fidList = []

        for i in friend_id:
        	if i.user_one in idList:
        		fidList.append(i.user_one)
        	elif i.user_two in idList:
        		fidList.append(i.user_two)


    return render_template('search.html', search_result=search_result, search=search, idList=fidList)


@app.route('/dashboard')
def dashboard():
	user = User.query.filter_by(email = session['email']).first()

	restorants = Restaurant.query.all()

	return render_template('dashboard.html', user=user, restorants=restorants)


@app.route('/add_restaurante', methods=['GET', 'POST'])
def add_restaurante():
	user = User.query.filter_by(email = session['email']).first()
	form = AddRestaurante()

	if request.method == 'POST':
		if form.validate() == False:
			return render_template('add_restourant.html', form=form, user=user)
		else:
			menu = form.name.data
			menu += '_menu'

			db.engine.execute("CREATE TABLE " + menu.lower() + " (id int NOT NULL AUTO_INCREMENT, name varchar(255), price int, description varchar(255), PRIMARY KEY (ID)); ")

			newrest = Restaurant(form.name.data, form.type.data, menu)
			db.session.add(newrest)
			db.session.commit()

			return redirect(url_for('dashboard'))
                 
	elif request.method == 'GET':
		return render_template('add_restourant.html', form=form, user=user)

@app.route('/remove_restourant/<id>')
def remove_restourant(id):
	table_name = Restaurant.query.filter(Restaurant.id == id).first()
	db.engine.execute("DROP TABLE " + table_name.menu.lower())

	Restaurant.query.filter(Restaurant.id == id).delete()
	db.session.commit()

	return redirect(url_for('dashboard'))


@app.route('/add_manager/<id>')
def add_manager(id):
	user = User.query.filter_by(email = session['email']).first()
	restourant = Restaurant.query.filter(Restaurant.id == id).first()

	# menadzeri odredjenog restorana
	r_managers = RestaurantManager.query.filter(RestaurantManager.restaurant == id).all()
	managerList = []

	for r_m in r_managers:
		managerList.append(r_m.manager)

	# menadzeri svih restorana
	all_managers = RestaurantManager.query.all()
	allManagerList = []

	for all_m in all_managers:
		allManagerList.append(all_m.manager)

	users_managers = User.query.filter(and_(User.email != session['email'], User.id.in_(managerList))).all()
	users_candidates = User.query.filter(and_(User.email != session['email'], not_(User.id.in_(allManagerList)))).all()


	return render_template('add_manager.html', user=user, restourant=restourant, users=users_managers, can=users_candidates)


@app.route('/add_user_as_manager/<u_id>/<r_id>')
def add_user_as_manager(u_id, r_id):
	user = User.query.filter_by(email = session['email']).first()
	restourant = Restaurant.query.filter(Restaurant.id == id).first()
	r_managers = RestaurantManager.query.filter(RestaurantManager.restaurant == id).all()
	managerList = []

	for r_m in r_managers:
		managerList.append(r_m.manager)

	users_managers = User.query.filter(and_(User.email != session['email'], User.id.in_(managerList))).all()
	users_candidates = User.query.filter(and_(User.email != session['email'], not_(User.id.in_(managerList)))).all()

	r = RestaurantManager(u_id, r_id)
	db.session.add(r)
	db.session.commit()


	return redirect(url_for('add_manager', id=r_id))



@app.route('/remove_user_as_manager/<u_id>/<r_id>')
def remove_user_as_manager(u_id, r_id):
	user = User.query.filter_by(email = session['email']).first()
	restourant = Restaurant.query.filter(Restaurant.id == r_id).first()

	RestaurantManager.query.filter(and_(RestaurantManager.manager == u_id, RestaurantManager.restaurant == r_id)).delete()
	db.session.commit()

	r_managers = RestaurantManager.query.filter(RestaurantManager.restaurant == id).all()
	managerList = []

	for r_m in r_managers:
		managerList.append(r_m.manager)

	users_managers = User.query.filter(and_(User.email != session['email'], User.id.in_(managerList))).all()
	users_candidates = User.query.filter(and_(User.email != session['email'], not_(User.id.in_(managerList)))).all()

	return redirect(url_for('add_manager', id=r_id))


@app.route('/manager_dashboard', methods=['GET', 'POST'])
def manager_dashboard():
	user = User.query.filter_by(email = session['email']).first()
	restaurant = RestaurantManager.query.filter(RestaurantManager.manager == user.id).first()
	rest = Restaurant.query.filter(Restaurant.id == restaurant.restaurant).first()

	menu_name = rest.name + "_menu"
	menu = db.engine.execute("SELECT * FROM " + menu_name.lower())

	if request.method == 'POST':
		item_name = request.form['naziv']
		item_description = request.form['opis']
		item_price = request.form['cena']

		if item_name == "" or item_description == "" or item_price == "":
			return render_template('restaurant_manager.html', user=user, restaurant=rest, menu=menu)
		else:
			newItem = db.engine.execute("INSERT INTO " + menu_name.lower() + " (id, name, price, description) VALUES (null, '" + item_name + "', " + item_price + ", '" + item_description + "')")
			#db.session.add(newItem)
			#db.session.commit()

			menu = db.engine.execute("SELECT * FROM " + menu_name.lower())

			return render_template('restaurant_manager.html', user=user, restaurant=rest, menu=menu)
	else:
		return render_template('restaurant_manager.html', user=user, restaurant=rest, menu=menu)



@app.route('/delete_menu_item/<id>/<item_id>')
def delete_menu_item(id, item_id):
	table_name = Restaurant.query.filter(Restaurant.id == id).first()
	db.engine.execute("DELETE FROM " + table_name.menu.lower() + " WHERE id = " + item_id)

	return redirect(url_for('manager_dashboard'))


@app.route('/edit_restaurant/<id>', methods=['GET', 'POST'])
def edit_restaurant(id):
	form = EditRestaurant()
	user = User.query.filter_by(email = session['email']).first()
	restaurant = RestaurantManager.query.filter(RestaurantManager.manager == user.id).first()
	rest = Restaurant.query.filter(Restaurant.id == restaurant.restaurant).first()

	if request.method == 'POST':
		#vrsi se izmena
		rest.name = form.name.data
		rest.type = form.type.data
		db.session.commit()

		return redirect(url_for('manager_dashboard'))
	else:
		return render_template('edit_restaurant.html', user=user, restaurant=rest, form=form)


@app.route('/rezervacija/<id>', methods=['GET', 'POST'])
def rezervacija(id):
	user = User.query.filter_by(email = session['email']).first()
	restaurant = Restaurant.query.filter(Restaurant.id == id).first()
	
	return render_template('rezervacija.html', user=user, restaurant=restaurant)






if __name__ == '__main__':
	app.run(debug=True)