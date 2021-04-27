{
    'name' : 'Institutes management system',
    'version' : 'v13.0',
    'description' : 'This system is used in training centers and institutes',
    'application' : True,
    'sequence' : -10,
    'author' : 'LG Company Eng: Moaz Noory Shami',
    'depends' : ['hr'],
    'image' : ['image/images.jpg'],
    'data' : [
        'secuirty/secuirty_group.xml',
        'reports/couser_report.xml',
        'reports/student_report.xml',
        'data/sequence.xml',
        'data/pay_sequence.xml',
        'views/view.xml'
    ],
}