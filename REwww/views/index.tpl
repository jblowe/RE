<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<meta name="description" content="reconstruction engine">
	<link rel="icon" href="/static/favicon.ico">		
	<title>The Reconstruction Engine</title>
	<link rel="stylesheet" type="text/css" href="/static/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="/static/bootstrap-sortable.css">
    <script type="text/javascript" src="/static/moment.min.js"></script>
	<script type="text/javascript" src="/static/jquery.min.js"></script>
    <script type="text/javascript" src="/static/bootstrap-sortable.js"></script>
	<script type="text/javascript" src="/static/bootstrap.min.js"></script>
</head>
<body>
	<!-- Static navbar -->
	<nav class="navbar navbar-default navbar-static-top">
		<div class="container">
			<div class="row">
				<div class="navbar-header">
					<button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
						<span class="sr-only">Toggle navigation</span>
						<span class="icon-bar"></span>
						<span class="icon-bar"></span>
						<span class="icon-bar"></span>
					</button>
					<a class="navbar-brand" href="#">The Reconstruction Engine</a>
				</div>
				<div id="navbar" class="navbar-collapse collapse">
					<ul class="nav navbar-nav navbar-right">
						<li><a href="/">Home</a></li>
						<li><a href="/about">About</a></li>
						<li><a href="/list_projects">Projects</a></li>
					</ul>
				</div><!--/.nav-collapse -->
			</div>
		</div>
	</nav>
	<div class="container">
		<div class="row">
			<div class="container-fluid">
            % if 'project' in data:
              <div id="project" class="col-sm-4">
                <a href="/list_projects">&lt;&lt; back</a>
                <h3>{{data['project']}}</h3>
                  % for (file_type, files) in data['files']:
                    <h5>{{file_type}}</h5>
                    <ul>
                      % for file in files:
                        <li><a href="/project_files/{{data['project']}}/{{file}}">{{file}}</a></li>
                      % end
                    </ul>
                  % end
              </div>
              % if 'content' in data:
                <div id="content" class="col-sm-8">
                <!-- a href="/project/{{data['project']}}">&lt;&lt; back</a -->
                <h3>{{data['filename']}}</h3>
                {{!data['content']}}
                </div>
              % end
            % elif 'projects' in data:
            <ul>
              % for project in data['projects']:
                <li><a href="/project/{{project}}">{{project}}</a></li>
              % end
            </ul>
            % elif 'home' in data:
			<h2>The Reconstruction Engine</h2>
				<p>
				A computer implementation of the comparative method.
				</p>
            % elif 'about' in data:
                % include('about.tpl')
            % end
		</div>
		<!--./row-->
		<div class="row">
			<hr>
			<footer>
				<p><i>Lowe, François, Mazaudon, and Zhang 2019.</i>  {{ footer_info }}</p>
			</footer>			
		</div>
	</div>
	<!-- /container -->
</body>
</html>