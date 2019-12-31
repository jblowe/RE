<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<meta name="description" content="reconstruction engine">
	<link rel="icon" href="/static/favicon.ico">
	<title>The Reconstruction Engine</title>

    <script src="/static/jquery.min.js"/>
    <script src="/static/bootstrap-table.min.js"></script>
	<link rel="stylesheet" type="text/css" href="/static/bootstrap.min.css">
    <link href="/static/bootstrap-table.min.css" rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="/static/all.min.css"/>
    <link rel="stylesheet" type="text/css" href="/static/mdb.min.css"/>
    <link rel="stylesheet" type="text/css" href="/static/reconengine.css"/>
    <style>
    .btn-xs {
        padding: .25rem .4rem;
        font-size: .875rem;
        line-height: .5;
        border-radius: .2rem;
    }
    .subheadr { padding-top: 8px; }
    .retable >tbody>tr>td{
      padding:0px;
      border-top: 0px;
    }
    .sets th { position: sticky; top: 0; background: white}

    .both { background-color: lightgreen; }
    .l1 { background-color: lightcoral; }
    .l2 { background-color: lightpink; }
    </style>
    <script>
    $(document).ready(function(){
      $("h6").click(function(){
        event.preventDefault();
        $(this).closest('h6').next('div').toggle();
      });
      // Treeview Initialization
      $('.treeview').mdbTreeview()
    });
    </script
    <script type="text/javascript" src="/static/moment.min.js"></script>
	<script type="text/javascript" src="/static/jquery.min.js"></script>
	<script type="text/javascript" src="/static/bootstrap.min.js"></script>
    <script type="text/javascript" src="/static/bootstrap-sortable.js"></script>
	<script type="text/javascript" src="/static/mdb.min.js"></script>
</head>