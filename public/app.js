$(document).ready(function() {
     var lock = new Auth0Lock(AUTH0_CLIENT_ID, AUTH0_DOMAIN, {
        theme: {
            logo: '../public/jessikaio_logo_gradient_small.png',
            primaryColor: '#6daedb',
            title: ""
        },
        container: 'lock-box',
        auth: {
          redirectUrl: AUTH0_CALLBACK_URL
        }
     });
     lock.show();
   
});
