% if not ('about' in data or 'home' in data or 'projects' in data):
<div style="float: right;">
    <a href="{{data['back']}}">&lt;&lt; back</a>
    <span style="padding-right: 20px;"> </span>
    <a href="#" id="toggle_sidebar">toggle sidebar</a>
</div>
%end
