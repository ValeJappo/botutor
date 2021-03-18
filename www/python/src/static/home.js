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

    //Define variables
    var isMsgOn=false; //Checks if there is already a warning message on the top of the page
    var msg_el; //Stores the current warning message's element

    //Toggle the warning message
    function toggle_alert(type, msg){
        if(!isMsgOn){
            //Create message widget
            msg_el=new OO.ui.MessageWidget( {
                type: type,
                label: msg
            } );
            isMsgOn=true;
            //Create close button
            close_btn=new OO.ui.ButtonWidget( {
                icon: 'close',
                label: 'Nascondi',
                invisibleLabel: true,
                framed: false,
                title: 'Nascondi messaggio'
            } );
            close_btn.on("click", function(){msg_el.$element.remove(); isMsgOn=false;});
            close_btn.$element.attr("style", "position:relative; top:-.35em; float:right");

            //Append
            msg_el.$icon.after(close_btn.$element);
            booklet.getCurrentPage().$element.prepend(msg_el.$element);
        }else{
            //Change current message
            msg_el.setType(type);
            msg_el.setLabel(msg);
        }
    }

    //Start following a user
    function segui(user, options){
        if (user!=""){
            options.forEach(function(item){
                //Fetch (see app.py for details on how follow works)
                fetch("/action/segui/"+user+"/"+item)
                .then(function(response){return response.json();})
                .then(function(response) {
                    //Return response in alert
                    if(response.status=='success')
                        toggle_alert("success", user+" aggiunto agli utenti osservati");
                    else if(response.status=='duplicate')
                        toggle_alert("warning", user+" fa già parte dei tuoi utenti osservati");
                    else if(response.status=='login')
                        toggle_alert("error", "Qualcosa è andato storto ed il tuo accesso con OAuth sembra essere scaduto. Prova a ricaricare la pagina.");
                    else
                        toggle_alert("error", "Errore nell'aggiungere "+user+" agli utenti osservati");
                });
            });
        }
    }

    //Stop following a user
    function rimuovi(user){
        if (user!=""){
            //Fetch (see app.py for details on how follow works)
            fetch("/action/segui/"+user+"/rimuovi")
                .then(function(response){return response.json();})
                .then(function(response) {
                    //Return response in alert
                    if(response.status=='success')
                        toggle_alert("success", user+" rimosso dagli utenti osservati");
                    else
                        toggle_alert("error", "Errore nel rimuovere "+user+" dagli utenti osservati");
                });
        }
    }

    //Create multi select widget
    var multiselect=new OO.ui.MenuTagMultiselectWidget( {
        selected: [
            {
                data: 'all',
                label: '(tutte le modifiche)'
            }
            ],
        options: [
            {
                data: 'all',
                label: '(tutte le modifiche)'
            },
            {
                data: 'talk',
                label: 'Modifiche alle pagine di discussione'
            },
            {
                data: 'ns0',
                label: 'Modifiche al namespace principale'
            },
            {
                data: 'sandbox',
                label: 'Modifiche alla sandbox'
            },
            {
                data: 'ping',
                label: 'Modifiche nella sua pagina di discussione senza template Ping'
            },
        ],
        classes: ['segui-tags']
    } );
    var save_loop=false; //variable to avoid entering a loop
    //On event change
    multiselect.on("change", function(items){
        if(items.length>0){ //If there are items
            if((items[items.length-1].data=="all" && items.length>1)){ //If the last one is 'all' and there are others selected

                //Unselect everything apart from 'all'
                multiselect.getMenu().items.forEach(function(i){
                    multiselect.getMenu().unselectItem(i);
                });
                multiselect.setValue(["all"]);

            }else if((multiselect.findItemFromData("all")!=null && items.length !=1)){ //If 'all' is selected and another item get selected
                //Unselect 'all'
                multiselect.removeTagByData("all");
                save_loop=true;
            }
        }
    });
    
    //Create a User-Lookup text input widget

    /*
    Adapted from DemoNumberLookupTextInputWidget
    https://gerrit.wikimedia.org/g/oojs/ui/+/master/demos/classes/NumberLookupTextInputWidget.js
    */

    UserLookupTextInputWidget = function UserLookupTextInputWidget( config ) {
        // Parent constructor
        OO.ui.TextInputWidget.call( this, $.extend( { validate: 'string'}, config ) );
        // Mixin constructors
        OO.ui.mixin.LookupElement.call( this, config );
    };
    OO.inheritClass( UserLookupTextInputWidget, OO.ui.TextInputWidget );
    OO.mixinClass( UserLookupTextInputWidget, OO.ui.mixin.LookupElement );

    UserLookupTextInputWidget.prototype.getLookupRequest = function () {
        var
            value = this.getValue(),
            deferred = $.Deferred();
        
        // Provide users as options
        this.getValidity().then( function () {
            // Resolve with API results
            var url = "https://it.wikipedia.org/w/api.php"; 
            var params = {
                "action": "query",
                "format": "json",
                "list": "allusers",
                "auprefix": value.charAt(0).toUpperCase() + value.slice(1)

            };
            url = url + "?origin=*";
            Object.keys(params).forEach(function(key){url += "&" + key + "=" + params[key];});
            fetch(url)
                .then(function(response){return response.json();})
                .then(function(response) {
                    var list=[];
                    //Add to list each user name
                    response.query.allusers.forEach(function(user){
                        list.push(user.name);
                    });
                    deferred.resolve(list);
                })
                .catch(function(error){console.log(error);});

        }, function () {
            // No results when the input contains invalid content
            deferred.resolve( [] );
        } );
        return deferred.promise( { abort: function () {} } );
    };

        UserLookupTextInputWidget.prototype.getLookupCacheDataFromResponse = function ( response ) {
        return response || [];
    };

        UserLookupTextInputWidget.prototype.getLookupMenuOptionsFromData = function ( data ) {
        var
            items = [],
            i, number;
        for ( i = 0; i < data.length; i++ ) {
            number = String( data[ i ] );
            items.push( new OO.ui.MenuOptionWidget( {
                data: number,
                label: number
            } ) );
        }
        return items;
    };

    //Create new fieldset layout
    var txtinput = new OO.ui.FieldsetLayout( {
        label: null,
        items: [
            new OO.ui.FieldLayout( new UserLookupTextInputWidget({
                icon: 'userAvatarOutline',
                autocomplete: false
            }), {
                align: 'top',
                label: 'Scegli un utente'
            } ),
            new OO.ui.FieldLayout( new OO.ui.Widget( {
                content: [
                    multiselect
                ]
            }),
            {
                align: 'top',
                label: "Seleziona le modifiche per le quali vuoi ricevere una notifica"
            }),
            new OO.ui.FieldLayout( new OO.ui.Widget( {
                content: [
                    new OO.ui.HorizontalLayout( {
                        items: [
                            new OO.ui.ButtonInputWidget( {
                                type: 'submit',
                                name: 'segui',
                                label: 'Segui',
                                flags: [
                                    'primary',
                                    'progressive'
                                ],
                                icon: 'userAdd',
                                classes: ['segui-add']
                            } ),
                            new OO.ui.ButtonWidget( {
                                framed: false,
                                flags: [
                                    'destructive'
                                ],
                                label: 'Smetti di seguire',
                                classes: [
                                    'segui-remove'
                                ]
                            } )
                        ]
                    } )
                ]
            } ), {
                align: 'top',
                label: null
            } )
        ]
    } );

    this.$element.append(txtinput.$element);

    txtinput.items[2].$element.find('.segui-add').on("click", function(){segui(txtinput.$element.find("input").val(), multiselect.getValue())});
    txtinput.items[2].$element.find('.segui-remove').on("click", function(){rimuovi(txtinput.$element.find("input").val())});

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