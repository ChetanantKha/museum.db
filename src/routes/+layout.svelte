<script>
	let {children} = $props();
</script>

<nav>
	<a href="/">Home</a>
	<a href="/collection">My collection</a>
	<a href="/artifacts">Artifact</a>
	<a href="/factions">Faction</a>
	<a href="/quiz">Quiz</a>
</nav>

<hr>

{@render children()}
