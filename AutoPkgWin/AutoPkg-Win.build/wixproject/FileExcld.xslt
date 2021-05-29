<?xml version="1.0" encoding="utf-8"?>
<!-- 
Transform to alter the output from heat.exe for AutoPkg
Main functions:
-Remove nssm.exe', 'AutoPkgTaskRunner.ps1' and 'AutopkgTaskrunnerCMD.apkcmd' from APfiles.wxs
Version 1.0, 20210513, Nick Heim, ETHZ, ID-CD
-->
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:wix="http://schemas.microsoft.com/wix/2006/wi"
	xmlns:msxsl="urn:schemas-microsoft-com:xslt" exclude-result-prefixes="msxsl">

		<!-- Identity Transform, match all elements -->
	<xsl:output method="xml" indent="yes"/>

	<!-- Identity Transform, match all elements (all attributes| any node other than an attribute node and the root node)-->
	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>

	<!-- Filter out the exe files -->
	<xsl:key name="exe-search" match="wix:Component[contains(wix:File/@Id, 'nssm.exe') or contains(wix:File/@Id, 'AutoPkgTaskRunner.ps1') or contains(wix:File/@Id, 'AutopkgTaskrunnerCMD.apkcmd')]" use="@Id" />
	<xsl:template match="wix:Component[key('exe-search', @Id)]" />
	<xsl:template match="wix:ComponentRef[key('exe-search', @Id)]" />

</xsl:stylesheet>
