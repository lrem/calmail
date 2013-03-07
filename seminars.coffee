$ ->
    $.getJSON 'https://www-sop.inria.fr/members/Remigiusz.Modrzejewski/seminars.json', (data) -> 
        content = '<div class="entry-content clearfix">'
        for e in data
            content += "
            <p>&nbsp;</p>
            <a href=\"#{e['URL']}\">#{e['AUTHOR']}</a>
            (#{e['AFFILIATION']})
            &mdash;
            #{e['DATE']}
            <blockquote>
            <p><strong>#{e['SUMMARY']}</strong></p>
            <p>
            #{e['ABSTRACT']}
            </p>
            </blockquote>"
        content += '</div>'
        div = $('div.entry-content')
        div.replaceWith content
