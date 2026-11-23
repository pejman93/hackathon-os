// The people on the page (fictional sample data). Portrait paths are relative to index.html.
// A person without a LinkedIn link renders as a plain card; without an image, as
// their initial. Mentors are listed by kind (tech or business), not by team.
// Keep the final card so prospective mentors can get in touch.
// index.html carries the same cards as a no-JavaScript fallback: keep both in step.
window.HACKATHON_TEAM = [
 {name:'Grace',role:'Tech Mentor',title:'AI Engineer',image:'assets/people/grace.jpg',linkedin:'https://example.org/profile'},
 {name:'Alan',role:'Tech Mentor',title:'Machine Learning Engineer',image:'assets/people/alan.jpg',linkedin:'https://example.org/profile'},
 {name:'Konrad',role:'Tech Mentor',title:'Software Developer',image:'assets/people/konrad.jpg',linkedin:'https://example.org/profile'},
 {name:'Katherine',role:'Business Mentor & Judge',title:'University Lecturer',image:'assets/people/katherine.jpg',linkedin:'https://example.org/profile'},
 {name:'Dorothy',role:'Business Mentor & Judge',title:'Business Consultant',image:'assets/people/dorothy.jpg',linkedin:'https://example.org/profile'},
 {name:'Charles',role:'Judge',title:'College President',image:'assets/people/charles.jpg',linkedin:'https://example.org/profile'},
 {name:'Emmy',role:'Judge',title:'College CEO',image:'assets/people/emmy.jpg',linkedin:'https://example.org/profile'},
 {name:'John',role:'Speaker & Panelist',title:'Keynote Speaker',image:'assets/people/john.jpg',linkedin:'https://example.org/profile',stagePortrait:true},
 {name:'Ada',role:'Hackathon Lead',title:'Hackathon Lead',image:'assets/people/ada.jpg',linkedin:'https://example.org/profile'},
 {unannounced:true,name:'More mentors',role:'Mentor the next one'}
];
