function PageOneLayout( name, config ) {
    PageOneLayout.super.call( this, name, config );
    var contacts_msg=new OO.ui.ButtonWidget( {
        icon: 'userTalk',
        label: "Contatti"
    } );
    var documentazione=new OO.ui.ButtonWidget( {
        label: 'Documentazione',
        icon: 'book'
    } );
    var codice=new OO.ui.ButtonWidget( {
        label: 'Codice',
        icon: 'code'
    } );
    this.$element.append( '<p>Pagina principale.</p>' );
    this.$element.append(documentazione.$element, contacts_msg.$element, codice.$element);
}
OO.inheritClass( PageOneLayout, OO.ui.PageLayout );
PageOneLayout.prototype.setupOutlineItem = function () {
    this.outlineItem.setLabel( 'Pagina principale' );
};

function PageTwoLayout( name, config ) {
    PageTwoLayout.super.call( this, name, config );
    this.$element.attr("id", "p-segui");
}
OO.inheritClass( PageTwoLayout, OO.ui.PageLayout );
PageTwoLayout.prototype.setupOutlineItem = function () {
    this.outlineItem.setLabel( 'Segui un utente' );
};

function PageThreeLayout( name, config ) {
    PageThreeLayout.super.call( this, name, config );
    this.$element.attr("id", "p-modifiche");
}
OO.inheritClass( PageThreeLayout, OO.ui.PageLayout );
PageThreeLayout.prototype.setupOutlineItem = function () {
    this.outlineItem.setLabel( 'Ultime modifiche' );
};
function PageFourLayout( name, config ) {
    PageFourLayout.super.call( this, name, config );
    this.$element.append( '<p>Pagina di test.</p>' );
}
OO.inheritClass( PageFourLayout, OO.ui.PageLayout );
PageFourLayout.prototype.setupOutlineItem = function () {
    this.outlineItem.$element.attr("style", "display:none;");

};

var page1 = new PageOneLayout( 'home' ),
    page2 = new PageTwoLayout( 'segui' ),
    page3 = new PageThreeLayout ('modifiche'),
    page4 = new PageFourLayout ('test');

var booklet = new OO.ui.BookletLayout( {
    outlined: true
} );

booklet.addPages( [ page1, page2, page3, page4 ] );
booklet.$element.css("margin-top", "3em");
$( document ).ready(function() {
    $( "#page" ).append( booklet.$element );
    $("#p-segui").append($("#segui"));
    $("#segui").attr("style", "");
    $("#p-modifiche").append($("#modifiche"));
    $("#modifiche").attr("style", "");
});
if(window.location.hash) {
    booklet.setPage(window.location.hash.replace("#", ""));
  }
var menu = new OO.ui.ButtonMenuSelectWidget( {
    icon: 'settings',
    label: 'Impostazioni',
    invisibleLabel: true,
    framed: false,
    title: 'Impostazioni',
    menu: {
        items: [
            new OO.ui.MenuOptionWidget( {
                data: 'a',
                label: 'First'
            } ),
            new OO.ui.MenuOptionWidget( {
                data: 'b',
                label: 'Second',
                indicator: 'clear'
            } ),
            new OO.ui.MenuOptionWidget( {
                data: 'c',
                label: 'Third'
            } ),
            new OO.ui.MenuOptionWidget( {
                data: 'c',
                label: 'The fourth option has an overly long label'
            } ),
            new OO.ui.MenuOptionWidget( {
                icon: 'feedback',
                data: 'd',
                label: 'The fifth option has an icon'
            } )
        ]
    }
} );
var wiki = new OO.ui.ToggleButtonWidget( {
    icon: 'logoWikipedia',
    title: 'torna su Wikipedia',
    label: 'torna su Wikipedia',
    invisibleLabel: true,
    framed: false,
    value: false
} );
wiki.on( "click", function() {window.open("https://it.wikipedia.org");wiki.setValue(false);});

var notifications =  new OO.ui.ToggleButtonWidget( {
    icon: 'bell',
    title: 'Notifiche',
    label: 'Notifiche',
    invisibleLabel: true,
    framed: false,
    flags: ['progressive'],
    value: false
} );
notifications.on("click", function(){
    var curwindow;
    function MyDialog( config ) {
        MyDialog.super.call( this, config );
    }
    OO.inheritClass( MyDialog, OO.ui.Dialog );
    MyDialog.static.name = 'myDialog';
    MyDialog.prototype.initialize = function () {
        MyDialog.super.prototype.initialize.call( this );
        this.content = new OO.ui.PanelLayout( { padded: true, expanded: false } );
        this.content.$element.append($("#notifications").html());
        close_btn=new OO.ui.ButtonWidget( {
            icon: 'close',
            label: 'Chiudi',
            invisibleLabel: true,
            framed: false,
            title: 'Chiudi popup'
        } );
        close_btn.on("click", function(){curwindow.closeWindow('myDialog');});
        this.content.$element.prepend(close_btn.$element);
        this.$body.append( this.content.$element );
    };
    MyDialog.prototype.getBodyHeight = function () {
        return this.content.$element.outerHeight( true );
    };
    var myDialog = new MyDialog( {
        size: 'larger'
    } );
    // Create and append a window manager, which opens and closes the window.
    var windowManager = new OO.ui.WindowManager();
    curwindow=windowManager;
    windowManager.on("closing", function(){notifications.setValue(false);});
    $( document.body ).append( windowManager.$element );
    windowManager.addWindows( [ myDialog ] );
    // Open the window!
    windowManager.openWindow( myDialog );
    console.log("notifications");
})


var logout = new OO.ui.ToggleButtonWidget( {
    icon: 'logOut',
    title: 'log-out',
    label: 'Log-out',
    invisibleLabel: true,
    framed: false,
    value: false
} );
logout.on("click", function(){window.open("logout", "_self");});

var sidebar_toggle = new OO.ui.ToggleButtonWidget( {
    icon: 'menu',
    title: 'Espandi/restringi menù',
    label: 'Espandi/restringi menù',
    invisibleLabel: true,
    framed: false,
    value: false
} );
sidebar_toggle.on("click", function(){booklet.toggleMenu()});
$( document ).ready(function() {
    var arr = [notifications, menu, logout, wiki];
    arr.forEach(function(item, index){
        item.$element.prependTo($(".header"));
        item.$element.attr("id", "menu-icon");
    });
    sidebar_toggle.$element.prependTo($(".header"));
    sidebar_toggle.$element.attr("id", "menu-icon-left");
});