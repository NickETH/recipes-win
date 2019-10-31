// GPO module for Mozilla products
// https://mozillagpo.sourceforge.io/
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.
// Author: Kardash Pavel 2014-2017
// Version: v1.2
// TB Registry paths changed to ETHZ standard. 20181107, Nick Heim

var EXPORTED_SYMBOLS = [ 'GPO' ];

const Cu = Components.utils;
const Cc = Components.classes;
const Ci = Components.interfaces;

var GPO = {
	appName : "",
	basePath : "",
	defaultPath : "",
	certPath : "",
	lockedPath : "",
	rmcertPath : "",
	app : "",
	console : "",
	reg : "",
	env : "",
	certdb : "",
	prefService : "",
	prefs: null,
	
	// User env
	username : "",
	userdomain : "",
	userdnsdomain : "",
	userprofile : "",
	computername : "",

	//Main function
	processPolicyPrefs : function(){
		try {
			//set locked preferences from computer GPO
			this.log("Process computer GPO Locked prefs");
			this.reg.open(this.reg.ROOT_KEY_LOCAL_MACHINE,this.basePath,this.reg.ACCESS_READ);
			if(this.reg.hasChild(this.lockedPath)){
				this.applyPolicy(this.reg.ROOT_KEY_LOCAL_MACHINE,true);
			}
			//set user preferences from computer GPO
			this.log("Process computer GPO Default prefs");
			this.reg.open(this.reg.ROOT_KEY_LOCAL_MACHINE,this.basePath,this.reg.ACCESS_READ);
			if(this.reg.hasChild(this.defaultPath)){
				this.applyPolicy(this.reg.ROOT_KEY_LOCAL_MACHINE,false);
			}
			//set locked preferences from user GPO
			this.log("Process user GPO Locked prefs");
			this.reg.open(this.reg.ROOT_KEY_CURRENT_USER,this.basePath,this.reg.ACCESS_READ);
			if(this.reg.hasChild(this.lockedPath)){
				this.applyPolicy(this.reg.ROOT_KEY_CURRENT_USER,true);
			}
			//set user preferences from user GPO
			this.log("Process user GPO Default prefs");
			this.reg.open(this.reg.ROOT_KEY_CURRENT_USER,this.basePath,this.reg.ACCESS_READ);
			if(this.reg.hasChild(this.defaultPath)){
				this.applyPolicy(this.reg.ROOT_KEY_CURRENT_USER,false);
			}
		}catch(ex){}
	},
	
	//Read and applyPolicy
	applyPolicy : function(type, locked){
		if(locked){
			// aplly locked policy
			this.reg.open(type, this.basePath + "\\" + this.lockedPath, this.reg.ACCESS_READ);
		}
		else{
			// apply default policy
			this.reg.open(type, this.basePath + "\\" + this.defaultPath, this.reg.ACCESS_READ);
		}
		for (var i = 0; i < this.reg.valueCount; i++)
		{
			var prefName = this.reg.getValueName(i);
			var Preference = this.readRegistryValue(prefName);
			this.writePrefValue(prefName, Preference, locked);
		}
		this.reg.close();
	},
	
	//Read value from registry
	readRegistryValue : function(value){
	  switch (this.reg.getValueType(value)) {
		case this.reg.TYPE_STRING:
			var val = this.reg.readStringValue(value)
			val = val.replace(/\%username\%/ig,this.username);
			val = val.replace(/\%userdomain\%/ig,this.userdomain);
			val = val.replace(/\%userdnsdomain\%/ig,this.userdnsdomain);
			val = val.replace(/\%userprofile\%/ig,this.userprofile);
			val = val.replace(/\%computername\%/ig,this.computername);
			return val;
		case this.reg.TYPE_BINARY:
			return this.reg.readBinaryValue(value);
		case this.reg.TYPE_INT:
			return this.reg.readIntValue(value);
		case this.reg.TYPE_INT64:
			return this.reg.readInt64Value(value);
	  }
	  // unknown type
	  return null;
	},

	//write value to preferences
	writePrefValue : function(name, value, locked){
		this.log("Preference(" + this.getType(name,value) + "): " + name + " = |" + value + "|");
		// is value exists
		if ( this.prefService.getBranch("").getPrefType(name) ) 
		{
			// is user defined value exists
			if (this.prefService.getBranch("").prefHasUserValue(name)) {
				if (!locked) {
					// don't touch user defined value
					return null;
				};
			};
		};
		if (this.prefService.getDefaultBranch("").prefIsLocked(name)) {
			this.prefService.getDefaultBranch("").unlockPref(name);
		};
		switch(this.getType(name, value))
		{
			case "string":
				value = unescape(encodeURIComponent(value));
				this.prefService.getDefaultBranch("").setCharPref(name, value);
				if(locked){
					this.prefService.getDefaultBranch("").lockPref(name, value);
				};
				break;
			case "int":
				this.prefService.getDefaultBranch("").setIntPref(name, value);
				if(locked){
					this.prefService.getDefaultBranch("").lockPref(name, value);
				};
				break;
			case "bool":
				if ( value.toLowerCase() == "false" ){
					this.prefService.getDefaultBranch("").setBoolPref(name, false);
				}else{
					this.prefService.getDefaultBranch("").setBoolPref(name, true);
				}
				if(locked){
					this.prefService.getDefaultBranch("").lockPref(name, value);
				};
				break;
			default:
				return false;
				break;
		};
		return true;
	},
	

	getType : function(name,value){
		switch(this.prefService.getDefaultBranch("").getPrefType(name))
		{
			case 128:
				// PREF_BOOL
				return "bool";
				break;
			case 64:
				// PREF_INT
				return "int";
				break;
			case 32:
				// PREF_STRING
				return "string";
				break;
		};
		// else case try detect preference type by value
		if ( value.toLowerCase() == "true" || value.toLowerCase() == "false" ){
			return "bool";
		}
		else
		{
			try
			{
				if (/^-?[0-9]+$/.test(value)){
					return "int";
				}
			}
			catch(ex){}
		}
		return "string";
	},



	// Import certs from policy
	importCerts : function(){
		// Cert import
		this.reg.open(this.reg.ROOT_KEY_LOCAL_MACHINE,this.basePath,this.reg.ACCESS_READ);
		if(this.reg.hasChild(this.certPath)){
			this.loadCerts(this.reg.ROOT_KEY_LOCAL_MACHINE)
		}
		this.reg.close();
		this.reg.open(this.reg.ROOT_KEY_CURRENT_USER,this.basePath,this.reg.ACCESS_READ);
		if(this.reg.hasChild(this.certPath)){
			this.loadCerts(this.reg.ROOT_KEY_CURRENT_USER)
		}
		this.reg.close();
		
		// Cert remove
		this.reg.open(this.reg.ROOT_KEY_LOCAL_MACHINE,this.basePath,this.reg.ACCESS_READ);
		if(this.reg.hasChild(this.rmcertPath)){
			this.rmCerts(this.reg.ROOT_KEY_LOCAL_MACHINE)
		}
		this.reg.close();
		this.reg.open(this.reg.ROOT_KEY_CURRENT_USER,this.basePath,this.reg.ACCESS_READ);
		if(this.reg.hasChild(this.rmcertPath)){
			this.rmCerts(this.reg.ROOT_KEY_CURRENT_USER)
		}
		this.reg.close();
	},
	
	// Import certs from GPO (registry)
	loadCerts : function(type){
		const beginCert = "-----BEGIN CERTIFICATE-----";
		const endCert = "-----END CERTIFICATE-----";
		
		this.reg.open(type,this.basePath + "\\" + this.certPath,this.reg.ACCESS_READ);
		for (var i = 0; i < this.reg.valueCount; i++)
		{
			var prefName = this.reg.getValueName(i);
			var certfile = this.readRegistryValue(prefName);
			
			if (certfile) {
				certfile = certfile.replace(/[\r\n]/g, "");
				var begin = certfile.indexOf(beginCert);
				var end = certfile.indexOf(endCert);
				var cert = certfile.substring(begin + beginCert.length, end);
				var CertTrust = "C,c,c";//trustSSL,trustEmail,trustObjSign
				try {
					this.log("Adding certificate " + prefName + ": " + cert);
					this.certdb.addCertFromBase64(cert, CertTrust, "");
				} catch (ex) {
					this.log("addCert failed: " + ex);
				} 
			}
		}
		this.reg.close();
	},
	
	
	rmCerts : function(type){ 
		const beginCert = "-----BEGIN CERTIFICATE-----";
		const endCert = "-----END CERTIFICATE-----";
		this.reg.open(type,this.basePath + "\\" + this.rmcertPath,this.reg.ACCESS_READ);
		for (var i = 0; i < this.reg.valueCount; i++) {
			var prefName = this.reg.getValueName(i);
			var certfile = this.readRegistryValue(prefName);
			if (certfile) {
				certfile = certfile.replace(/[\r\n]/g, "");
				var begin = certfile.indexOf(beginCert);
				var end = certfile.indexOf(endCert);
				var cert = certfile.substring(begin + beginCert.length, end);
				var crt = this.certdb.constructX509FromBase64(cert);
				// Need two args. Second can be null.
				var ffCert = this.certdb.findCertByDBKey(crt.dbKey, null);
				this.log("Removing " + prefName + " certificate: " + ffCert.commonName);
				try {
					this.certdb.deleteCertificate(ffCert);
				} catch (ex) {
					this.log("rmCert failed: " + ex); 
				}
			}
		}
		this.reg.close();
	 },
	
	// enable logging by default
	defaultEnableLog : function(name,value){
		// is value exists
		if ( this.prefs.getPrefType("enablelog") )
		{
			// is user defined value exists
			if (this.prefs.prefHasUserValue("enablelog")) {
				// don't touch user defined value
				return null;
			};
		};
		this.prefs.setBoolPref("enablelog", true);
	},
	
	log : function(string) {
		if(this.prefs.getBoolPref("enablelog")) {
			this.console.logStringMessage("GPO: " + string);
		}
	},
	
	onLoad : function(){
	
		//load XPCOM component to work with console
		this.console = Components.classes["@mozilla.org/consoleservice;1"].getService(Components.interfaces.nsIConsoleService);
		//load XPCOM component to work with appInfo
		this.app = Components.classes["@mozilla.org/xre/app-info;1"].getService(Components.interfaces.nsIXULAppInfo);



		



		// running under Thunderbird
			this.appName = "Thunderbird";














			
		//load XPCOM component to read registry
		this.reg = Components.classes["@mozilla.org/windows-registry-key;1"].createInstance(Components.interfaces.nsIWindowsRegKey);
		//load XPCOM component to read and write preferences
		this.prefService = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefService);
		//load XPCOM component to read user environment
		this.env = Components.classes["@mozilla.org/process/environment;1"].getService(Components.interfaces.nsIEnvironment);
		//load XPCOM component to work with certdb
		this.certdb = Components.classes["@mozilla.org/security/x509certdb;1"].getService(Components.interfaces.nsIX509CertDB); 
		
		//Branch to work with addon prefs
		this.prefs = this.prefService.getBranch("extensions.this.");
		this.defaultEnableLog();
		
		
		this.log("Detected application name: " + this.appName);
		




		
		//Define path where to read registry
		this.basePath = "Software\\Policies";
		
		this.log("Will read settings from registry branch: " + this.basePath + "\\" + this.appName);
		
//		this.defaultPath = this.appName + "\\defaultPref";
		this.defaultPath = this.appName;
		this.lockedPath = this.appName + "\\locked";
		this.certPath = this.appName + "\\addCACerts";
		this.rmcertPath = this.appName + "\\removeCACerts";
		
		this.username = this.env.get("USERNAME");
		this.userdomain = this.env.get("USERDOMAIN");
		this.userdnsdomain = this.env.get("USERDNSDOMAIN");
		this.userprofile = this.env.get("USERPROFILE");
		this.computername = this.env.get("COMPUTERNAME");

		this.log("lockedPath: " + this.lockedPath);
		this.processPolicyPrefs();
		this.importCerts();
		this.writePrefValue("distribution.about", "Managed with mozillagpo v1.2 module https://mozillagpo.sourceforge.io/", true);
		return;
	},
};
