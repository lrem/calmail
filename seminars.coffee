$ ->
    $.getJSON 'https://www-sop.inria.fr/members/Remigiusz.Modrzejewski/seminars.json', (data) -> 
        content = '
        <div class="entry-content clearfix">
        <p>To automatically add seminars to your calendar application, you can
        register the following calendar (ICS format): <a href=
        "https://zimbra.inria.fr/home/remigiusz.modrzejewski@inria.fr/Seminars">
        https://zimbra.inria.fr/home/remigiusz.modrzejewski@inria.fr/Seminars</a>
        </p>
        <h2>Upcoming</h2>'
        upcoming = true
        for e in data
            past  = (new Date().getTime()/1000 > e['EPOCH'])
            if upcoming and past
                content += "<h2>Past</h2>"
                upcoming = false
            slides = if not e['SLIDES'] then '' else \
                "<p><a href=\"#{e['SLIDES']}\">Slides</a></p>"
            content += "
            <p>&nbsp;</p>
            <a href=\"#{e['URL']}\">#{e['AUTHOR']}</a>
            (#{e['AFFILIATION']})
            &mdash;
            #{e['DATE']}
            <blockquote>
            <p><strong>#{e['SUMMARY']}</strong></p>
            #{slides}
            <p>
            #{e['ABSTRACT']}
            </p>
            </blockquote>
            <p>Room: #{e['LOCATION']}</p>"
        content += '</div>'
        div = $('div.entry-content')
        div.replaceWith content
