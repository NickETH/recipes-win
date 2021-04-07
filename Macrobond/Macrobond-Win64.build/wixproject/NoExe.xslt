<?xml version="1.0" encoding="utf-8"?>
<!-- 
Transform to alter the output from heat.exe for Element
Main functions:
-Remove the "Element.exe", it is contained in Element.wxs
Version 1.0, 20210317, Nick Heim, ETHZ, ID-CD
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

	<!-- Filter out the exe file -->
	<xsl:key name="exe-search" match="wix:Component[contains(wix:File/@Id, 'Element.exe')]" use="@Id" />
	<xsl:template match="wix:Component[key('exe-search', @Id)]" />
	<xsl:template match="wix:ComponentRef[key('exe-search', @Id)]" />

</xsl:stylesheet>
