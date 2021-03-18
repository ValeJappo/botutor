// Create Main page
function HomePage( name, config ) {
    HomePage.super.call( this, name, config );
    var contacts_msg=new OO.ui.ButtonWidget( {
        icon: 'userTalk',
        label: "Contatti",
        href: "#contacts"
    } );
    var documentazione=new OO.ui.ButtonWidget( {
        label: 'Documentazione',
        icon: 'book',
        href: "#docs"
    } );
    var codice=new OO.ui.ButtonWidget( {
        label: 'Codice',
        icon: 'code',
        href: '#code'
    } );
    this.$element.append( '<p>Pagina principale.</p>' );
    this.$element.append(documentazione.$element, contacts_msg.$element, codice.$element);
}
OO.inheritClass( HomePage, OO.ui.PageLayout );
HomePage.prototype.setupOutlineItem = function () {
    this.outlineItem.setLabel( 'Pagina principale' );
};

//Create Follow page
function FollowPage( name, config ) {
    FollowPage.super.call( this, name, config );
    this.$element.attr("id", "p-segui");
}
OO.inheritClass( FollowPage, OO.ui.PageLayout );
FollowPage.prototype.setupOutlineItem = function () {
    this.outlineItem.setLabel( 'Segui un utente' );
};

// Create Recent changes page
function ChangesPage( name, config ) {
    ChangesPage.super.call( this, name, config );
    this.$element.attr("id", "p-modifiche");
}
OO.inheritClass( ChangesPage, OO.ui.PageLayout );
ChangesPage.prototype.setupOutlineItem = function () {
    this.outlineItem.setLabel( 'Ultime modifiche' );
};

//Create Test page
function TestPage( name, config ) {
    TestPage.super.call( this, name, config );
    this.$element.append( '<p>Pagina di test.</p>' );
}
OO.inheritClass( TestPage, OO.ui.PageLayout );
TestPage.prototype.setupOutlineItem = function () {
    this.outlineItem.setLabel( 'Pagina di test' );
    this.outlineItem.$element.attr("style", "display:none;");
    this.outlineItem.$element.addClass("unlisted");
};

function DocsPage( name, config ) {
    DocsPage.super.call( this, name, config );
    this.$element.append( '<h1>Documentazione</h1>' );
}
OO.inheritClass( DocsPage, OO.ui.PageLayout );
DocsPage.prototype.setupOutlineItem = function () {
    this.outlineItem.setLabel( 'Documentazione' );
    this.outlineItem.$element.attr("style", "display:none;");
    this.outlineItem.$element.addClass("unlisted");
};

//Add pages into variables
var page1 = new HomePage( 'home' ),
    page2 = new FollowPage( 'segui' ),
    page3 = new ChangesPage ('modifiche'),
    page4 = new TestPage ('test'),
    page5 = new DocsPage ('docs');

//Create booklet layout
var booklet = new OO.ui.BookletLayout( {
    outlined: true
} );

booklet.addPages( [ page1, page2, page3, page4, page5 ] );
booklet.$element.css("margin-top", "3em");
$( document ).ready(function() {
    $( "#page" ).append( booklet.$element );
    $("#p-segui").append($("#segui"));
    $("#segui").attr("style", "");
    $("#p-modifiche").append($("#modifiche"));
    $("#modifiche").attr("style", "");
});

// Get page changes
var lastUnlisted="";
booklet.on("set", function(page){
    //Remove current url hash
    
    if(window.history.pushState) {
        window.history.pushState('', '/', window.location.pathname)
    } else {
        window.location.hash = '';
    }
    
    //Toggle button's visibility if unlisted
    if (lastUnlisted!="" && lastUnlisted!=page.name){
        console.log(lastUnlisted);
        booklet.getPage(lastUnlisted).outlineItem.$element.attr("style", "display:none;");
        lastUnlisted="";
    }
    if(booklet.getPage(page.name).outlineItem.$element.hasClass("unlisted") && lastUnlisted!=page.name){
        console.log(page.name);
        booklet.getPage(page.name).outlineItem.$element.attr("style", "");
        lastUnlisted=page.name
    }
});

// Get url hash
function hash(){
    console.log(window.location.hash)
    if(window.location.hash) // Change page
        booklet.setPage(window.location.hash.replace("#", ""));
}
hash();
window.onhashchange = function(){hash()};


//Create Header's buttons
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
    // Create and append a window manager, which opens and closes the window
    var windowManager = new OO.ui.WindowManager();
    curwindow=windowManager;
    windowManager.on("closing", function(){notifications.setValue(false);});
    $( document.body ).append( windowManager.$element );
    windowManager.addWindows( [ myDialog ] );
    // Open the window
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
//Append buttons
$( document ).ready(function() {
    var arr = [notifications, menu, logout, wiki];
    arr.forEach(function(item, index){
        item.$element.prependTo($(".header"));
        item.$element.attr("id", "menu-icon");
    });
    sidebar_toggle.$element.prependTo($(".header"));
    sidebar_toggle.$element.attr("id", "menu-icon-left");
});