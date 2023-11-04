# dash-app
`dash-app` makes a Dash interface available through an parameterizable url. 

The main feature is having a scatter-plot populated with x and y data, and on top 
of that, have a collection of N (user defined) points, all connected by lines, which
the user is able to freely manipulate, in terms of their position.

Initially the dash app needs to fetch the x and y data, as well as the parameters of 
each point, from a redis server.

The user is then able to freely manipulate the position of each point, which in turn 
is sent back to the redis server. 

We use this app in the context of the power curve cleaning tool, which requires a set
of 4-5 points, which uses to make cleaning operations on a dataset.


An example of a valid url would be:

http://0.0.0.0:8050/dash?uuid=12345&assets=A01,A02,A03&x_name=active_power&y_name=wind_speed&points=point_1,point_2,point_3&stages=original

1. uuid - a unique identifier which is used to fetch unique data from the redis server.
2. assets - a list of assets, from which data from redis will be fetch, and which will be displayed
in the dash app.
3. x_name - name of the x axis.
4. y_name - name of the y axis.
5. points - a list with the names of the points which are to be fetch from redis, and
displayed in the dash app.
6. stages - a list of data 'stages' which can be fetch from redis, data from different
stages will be displayed with different colors in the dash app.

To be more specific on how the dash app retrieves a point from the redis server.It
looks for keys in this format:

    "{uuid}:{point_name}.x"
    "{uuid}:{point_name}.y"
In order to fetch both x and y parameters for a certain point.

To be more specific on how the dash app retrieves axis data from the redis server.
It looks for keys in this format:

    f"{uuid}:{asset}:{x_name}:{stage}"

