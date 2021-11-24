<?xml version="1.0" encoding="utf-8"?>
<!-- 
Transform to alter the output from heat.exe
Main function(s):
Insert the Win64 attribute into all "Component"-elements
Version 1.0, 20190730, Nick Heim, ETHZ, ID-CD
-->
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:wix="http://schemas.microsoft.com/wix/2006/wi"
	xmlns:msxsl="urn:schemas-microsoft-com:xslt" exclude-result-prefixes="msxsl">

	<xsl:output method="xml" indent="yes"/>

	<!-- Identity Transform, match all elements -->
	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>
	
	<!-- Match all the Components and add the Win64 attribute -->
	<xsl:template match="wix:Component">
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<!-- Insert the Win64-attribute -->
			<xsl:attribute name="Win64">yes</xsl:attribute>
			<!-- Copy the child elements from the new Component. -->
			<xsl:copy-of select="node()" />
		</xsl:copy>
	</xsl:template>
	
</xsl:stylesheet>
